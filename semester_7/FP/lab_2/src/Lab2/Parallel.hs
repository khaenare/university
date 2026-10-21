-- | Thread helpers shared by the parallel algorithms.
--
-- Workers are ordinary Haskell threads started with 'forkOn'; with the
-- threaded runtime (@-threaded@, @+RTS -N@) they run on different cores.
module Lab2.Parallel
  ( maxWorkers
  , workerCount
  , Stop
  , stopRequested
  , runWorkers
  , parallelSearch
  , splitRange
  , blockSize
  , Hit (..)
  , BlockScan
  , scanRange
  , geometricScan
  , parallelGeometricScan
  ) where

import Control.Concurrent (forkOn, getNumCapabilities, killThread)
import Control.Concurrent.MVar (newEmptyMVar, putMVar, takeMVar)
import Control.Exception (SomeException, mask, onException, throwIO, try)
import Control.Monad (forM, forM_)
import Data.IORef (IORef, atomicModifyIORef', atomicWriteIORef, newIORef, readIORef)

import Lab2.Arith (isSmallModulus, mulMod, mulModLarge, mulModSmall, powMod)

-- | Upper limit of worker threads. Some bookkeeping (the buckets of the
-- baby-step table) grows with the square of the thread count.
maxWorkers :: Int
maxWorkers = 1024

-- | The number of workers actually used for a requested count: at least
-- one and at most 'maxWorkers'. Every parallel function applies it, so a
-- count of 0 cannot silently mean "no solution".
workerCount :: Int -> Int
workerCount = max 1 . min maxWorkers

-- | Shared flag that asks the workers to finish early.
newtype Stop = Stop (IORef Bool)

stopRequested :: Stop -> IO Bool
stopRequested (Stop flag) = readIORef flag

-- | Run workers @0 .. k-1@, each pinned to a capability, and wait for all
-- of them. An exception in a worker is re-thrown after all have finished.
-- If the waiting thread itself is interrupted (for example by a timeout),
-- the workers are killed instead of being left running.
runWorkers :: Int -> (Int -> IO ()) -> IO ()
runWorkers requested work = do
  caps <- getNumCapabilities
  let k = workerCount requested
  -- Masked so that no worker can be started but not yet recorded.
  results <- mask $ \restore -> do
    workers <- forM [0 .. k - 1] $ \i -> do
      done <- newEmptyMVar
      thread <- forkOn (i `mod` caps) (try (restore (work i)) >>= putMVar done)
      pure (thread, done)
    restore (mapM (takeMVar . snd) workers)
      `onException` mapM_ (killThread . fst) workers
  forM_ results (either (throwIO :: SomeException -> IO ()) pure)

-- | Run @k@ searching workers. The first worker that finds a value stores
-- it and asks the others to stop; the value is returned when all are done.
parallelSearch :: Int -> (Int -> Stop -> IO (Maybe a)) -> IO (Maybe a)
parallelSearch k worker = do
  flag <- newIORef False
  found <- newIORef Nothing
  runWorkers (workerCount k) $ \i -> do
    -- A failing worker also stops the others, so the caller is not kept waiting.
    result <- worker i (Stop flag) `onException` atomicWriteIORef flag True
    forM_ result $ \x -> do
      atomicModifyIORef' found (\old -> (maybe (Just x) Just old, ()))
      atomicWriteIORef flag True
  readIORef found

-- | Split @[0, n)@ into @k@ contiguous ranges of almost equal length.
splitRange :: Word -> Int -> [(Word, Word)]
splitRange n k = [(bound i, bound (i + 1)) | i <- [0 .. k - 1]]
  where
    bound i = fromIntegral (toInteger n * toInteger i `div` toInteger k)

-- | Number of consecutive indices a worker checks before it looks at the
-- stop flag and moves on to its next block.
blockSize :: Word
blockSize = 65536

-- | Index and value of the element that passed the test.
--
-- The fields are unpacked, so the hot loop below keeps the index as a raw
-- machine word and does not allocate on every step.
data Hit = Hit {-# UNPACK #-} !Word {-# UNPACK #-} !Word | Miss

-- | Searches the indices @[lo, hi)@ of a sequence, given @lo@, @hi@ and
-- the element at @lo@.
--
-- Each algorithm defines its own top-level 'BlockScan' (with 'scanRange'
-- inlined): the hot loop then gets its parameters in registers, while the
-- parallel driver below calls it only once per block.
type BlockScan = Word -> Word -> Word -> Hit

-- | Search the sequence @y_i = start * ratio^i (mod p)@ for @i@ in
-- @[lo, hi)@, beginning with @y = y_lo@, for the first @y_i@ that passes
-- @isHit@.
scanRange :: Word -> Word -> (Word -> Bool) -> BlockScan
scanRange p ratio isHit lo hi y0
  -- The modulus size is tested once; each branch gets its own copy of the
  -- loop with a fixed multiplication.
  | isSmallModulus p = scanWith mulModSmall
  | otherwise = scanWith mulModLarge
  where
    scanWith mul = go y0 lo
      where
        go !y !i
          | i >= hi = Miss
          | isHit y = Hit i y
          | otherwise = go (mul y ratio p) (i + 1)
    {-# INLINE scanWith #-}
{-# INLINE scanRange #-}

-- | Sequential search over @i = 0 .. count-1@ of a sequence starting with
-- @start@; returns the index and the value of the first hit.
geometricScan :: Word -> Word -> BlockScan -> Maybe (Word, Word)
geometricScan start count scan = case scan 0 count start of
  Hit i y -> Just (i, y)
  Miss -> Nothing

-- | Parallel version of 'geometricScan' for the sequence
-- @y_i = start * ratio^i (mod p)@.
--
-- The indices are cut into blocks of 'blockSize'; worker @w@ takes blocks
-- @w, w + k, w + 2k, ...@ (round robin). All workers therefore move through
-- the range together, and the answer at index @i@ is reached after about
-- @i / k@ steps of each worker wherever @i@ lies.
parallelGeometricScan :: Int -> Word -> Word -> Word -> Word -> BlockScan -> IO (Maybe (Word, Word))
parallelGeometricScan requested p start ratio count scan = parallelSearch k worker
  where
    -- The jump below must agree with the number of workers that really run.
    k = workerCount requested
    kw = fromIntegral k
    -- Moves the sequence from the start of a block to the start of the
    -- worker's next block, k blocks further.
    jump = powMod ratio (kw * blockSize) p
    worker w stop = go first (mulMod start (powMod ratio first p) p)
      where
        first = fromIntegral w * blockSize
        go !lo !y
          | lo >= count = pure Nothing
          | otherwise = do
              halt <- stopRequested stop
              if halt
                then pure Nothing
                else case scan lo (min count (lo + blockSize)) y of
                  Hit i yi -> pure (Just (i, yi))
                  Miss -> go (lo + kw * blockSize) (mulMod y jump p)
