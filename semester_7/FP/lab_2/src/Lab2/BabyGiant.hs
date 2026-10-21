-- | Shanks' baby-step giant-step algorithm.
--
-- With @m = ceil (sqrt n)@ every @x < n@ is @x = i*m + j@ with @i, j < m@,
-- and @g^x = h@ becomes @g^j = h * (g^-m)^i@. The "baby steps" @g^j@ are
-- stored in a sorted table; the "giant steps" @h * (g^-m)^i@ are looked up
-- in it. Time and memory are @O(sqrt n)@.
module Lab2.BabyGiant
  ( maxOrder
  , babyGiant
  , parallelBabyGiant
  ) where

import Control.Monad (forM, forM_)
import Control.Monad.ST (runST)
import Data.Maybe (isJust)
import Data.Ord (comparing)
import qualified Data.Vector.Algorithms.Intro as Intro
import qualified Data.Vector.Unboxed as U
import qualified Data.Vector.Unboxed.Mutable as UM

import Lab2.Arith (ceilSqrt, mulMod, powMod)
import Lab2.Parallel (BlockScan, geometricScan, parallelGeometricScan, runWorkers, scanRange, splitRange, workerCount)
import Lab2.Problem (Problem (..))

-- | Largest group order accepted by the command line: the table then has
-- 2^23 entries of 16 bytes, i.e. 128 MB. The parallel version also needs a
-- second array of the same size while it builds the table (256 MB at peak).
maxOrder :: Word
maxOrder = 2 ^ (46 :: Int)

-- | Baby steps @(g^j, j)@ for @j < m@, sorted by the first component.
-- The values are distinct because @m <= n@.
newtype BabyTable = BabyTable (U.Vector (Word, Word))

-- | Binary search for the @j@ with @g^j = y@.
lookupBaby :: BabyTable -> Word -> Maybe Word
lookupBaby (BabyTable table) y = go 0 (U.length table)
  where
    go lo hi
      | lo >= hi = Nothing
      | otherwise =
          let mid = (lo + hi) `quot` 2
              (key, j) = U.unsafeIndex table mid
           in case compare key y of
                EQ -> Just j
                LT -> go (mid + 1) hi
                GT -> go lo mid

-- | Sequential baby-step giant-step.
babyGiant :: Problem -> Maybe Word
babyGiant pr@(Problem p g _ n) =
  geometricScan (target pr) m (scanGiant p (giantRatio pr m) table) >>= answer pr m table
  where
    m = ceilSqrt n
    -- Filled in place, so there is no second copy of the table.
    table = runST $ do
      steps <- UM.new (fromIntegral m)
      let fill j y
            | j >= m = pure ()
            | otherwise = UM.unsafeWrite steps (fromIntegral j) (y, j) >> fill (j + 1) (mulMod y g p)
      fill 0 1
      Intro.sortBy (comparing fst) steps
      BabyTable <$> U.unsafeFreeze steps

-- | Baby-step giant-step with @k@ worker threads: both the table and the
-- giant steps are computed in parallel.
parallelBabyGiant :: Int -> Problem -> IO (Maybe Word)
parallelBabyGiant k pr@(Problem p _ _ n) = do
  table <- parallelTable k pr m
  let ratio = giantRatio pr m
  hit <- parallelGeometricScan k p (target pr) ratio m (scanGiant p ratio table)
  pure (hit >>= answer pr m table)
  where
    m = ceilSqrt n

-- | Giant step factor @g^-m@, computed as @g^(n-m)@ because @g^n = 1@
-- (and @m <= n@).
giantRatio :: Problem -> Word -> Word
giantRatio (Problem p g _ n) m = powMod g (n - m) p

-- | Look for giant steps (multiplying by @ratio = g^-m@) that are in the table.
scanGiant :: Word -> Word -> BabyTable -> BlockScan
scanGiant p ratio table = scanRange p ratio (isJust . lookupBaby table)
{-# NOINLINE scanGiant #-}

-- | Giant step @i@ has the value @y = h * g^(-m*i)@; if it equals baby step
-- @j@, then @x = i*m + j@ (reduced modulo @n@, the order of @g@).
answer :: Problem -> Word -> BabyTable -> (Word, Word) -> Maybe Word
answer pr m table (i, y) = (\j -> (i * m + j) `rem` order pr) <$> lookupBaby table y

-- | Build the sorted table in parallel without a final merge (bucket sort).
--
-- Residues are spread evenly over @[1, p)@, so the key range is cut into
-- @k@ equal buckets:
--
-- 1. each worker computes its share of the baby steps and counts how many
--    fall into each bucket;
-- 2. prefix sums of the counts give every worker its own place in every
--    bucket;
-- 3. each worker copies its steps into those places;
-- 4. each worker sorts one bucket. Bucket @b@ only holds keys smaller than
--    those of bucket @b + 1@, so the whole array is then sorted.
parallelTable :: Int -> Problem -> Word -> IO BabyTable
parallelTable requested (Problem p g _ _) m = do
  let k = workerCount requested
      ranges = splitRange m k
      width = p `quot` fromIntegral k + 1
      bucketOf key = fromIntegral (key `quot` width) :: Int
  raw <- UM.new (fromIntegral m)
  counts <- forM ranges (const (UM.replicate k (0 :: Int)))
  -- Step 1.
  runWorkers k $ \w -> do
    let (lo, hi) = ranges !! w
        count = counts !! w
        go j y
          | j >= hi = pure ()
          | otherwise = do
              UM.unsafeWrite raw (fromIntegral j) (y, j)
              UM.unsafeModify count (+ 1) (bucketOf y)
              go (j + 1) (mulMod y g p)
    go lo (powMod g lo p)
  -- Step 2. Worker w starts each bucket where workers 0 .. w-1 end.
  perWorker <- mapM U.freeze counts
  let bucketSizes = foldr (U.zipWith (+)) (U.replicate k 0) perWorker
      bucketStarts = U.prescanl (+) 0 bucketSizes
  cursors <- mapM U.thaw (take k (scanl (U.zipWith (+)) bucketStarts perWorker))
  -- Step 3.
  sorted <- UM.new (fromIntegral m)
  runWorkers k $ \w -> do
    let (lo, hi) = ranges !! w
        cursor = cursors !! w
    forM_ [fromIntegral lo .. fromIntegral hi - 1] $ \i -> do
      entry@(key, _) <- UM.unsafeRead raw i
      let b = bucketOf key
      pos <- UM.unsafeRead cursor b
      UM.unsafeWrite sorted pos entry
      UM.unsafeWrite cursor b (pos + 1)
  -- Step 4.
  runWorkers k $ \b ->
    sortSlice (UM.slice (bucketStarts U.! b) (bucketSizes U.! b) sorted)
  BabyTable <$> U.unsafeFreeze sorted

sortSlice :: UM.IOVector (Word, Word) -> IO ()
sortSlice = Intro.sortBy (comparing fst)
