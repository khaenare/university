-- | Pollard's rho method for discrete logarithms.
--
-- A pseudo-random walk over elements @y = g^a * h^b@ keeps track of the
-- exponents @a@ and @b@. Two different walks (or one walk and itself) that
-- reach the same element give @g^a h^b = g^a' h^b'@, which is solved for
-- @x@ ('solveRelation'). By the birthday paradox a collision is expected
-- after about @sqrt (pi * n / 2)@ steps, with almost no memory.
module Lab2.PollardRho
  ( pollardRho
  , parallelPollardRho
  ) where

import Data.Bits (shiftL, shiftR, (.&.))
import Data.IORef (atomicModifyIORef', newIORef)
import qualified Data.Map.Strict as Map
import qualified Data.Vector.Unboxed as U
import System.Random (StdGen, mkStdGen, uniformR)

import Lab2.Arith (addMod, isSmallModulus, log2, mulMod, mulModLarge, mulModSmall, powMod)
import Lab2.BruteForce (bruteForce)
import Lab2.Parallel (Stop, parallelSearch, stopRequested)
import Lab2.Problem (Problem (..), hasSolution, solveRelation)

-- | Groups this small are solved by exhaustive search instead.
smallOrder :: Word
smallOrder = 2 ^ (16 :: Int)

-- | Element of the walk with its exponents: @y = g^a * h^b@.
data Point = Point !Word !Word !Word

-- | Random starting point of a walk.
randomPoint :: Problem -> StdGen -> (Point, StdGen)
randomPoint (Problem p g h n) gen0 =
  (Point (mulMod (powMod g a p) (powMod h b p) p) a b, gen2)
  where
    (a, gen1) = uniformR (0, n - 1) gen0
    (b, gen2) = uniformR (0, n - 1) gen1

-- Sequential version ---------------------------------------------------------

-- | Pollard's original method: the walk splits the group into three
-- classes by @y mod 3@ and Floyd's cycle finding compares a slow walk
-- ("tortoise", one step) with a fast one ("hare", two steps) until they meet.
-- The seed chooses the random starting points.
pollardRho :: Int -> Problem -> Maybe Word
pollardRho seed pr
  | not (hasSolution pr) = Nothing
  | order pr < smallOrder = bruteForce pr
  | otherwise = attempt (mkStdGen seed)
  where
    attempt gen =
      let (start, gen') = randomPoint pr gen
       in case floyd (step start) (step (step start)) of
            Just x -> Just x
            -- A useless collision (for example b = b'): restart elsewhere.
            Nothing -> attempt gen'
    floyd tortoise@(Point y a b) hare@(Point y' a' b')
      | y == y' = solveRelation pr a b a' b'
      | otherwise = floyd (step tortoise) (step (step hare))
    step (Point y a b) = case y `rem` 3 of
      0 -> Point (mulMod y y p) (addMod a a n) (addMod b b n)
      1 -> Point (mulMod y h p) a (addMod b 1 n)
      _ -> Point (mulMod y g p) (addMod a 1 n) b
    Problem p g h n = pr

-- Parallel version -----------------------------------------------------------

-- | The parallel walk adds one of these precomputed elements
-- @g^(c_s) * h^(d_s)@ at each step ("r-adding walk", Teske).
partitions :: Int
partitions = 32

data Walk = Walk
  { stepElements :: !(U.Vector Word)
  , stepA :: !(U.Vector Word)
  , stepB :: !(U.Vector Word)
  }

randomWalk :: Problem -> StdGen -> Walk
randomWalk (Problem p g h n) gen0 = Walk (U.fromList elements) (U.fromList cs) (U.fromList ds)
  where
    exponents = take (2 * partitions) (randoms gen0)
    randoms gen = let (v, gen') = uniformR (0, n - 1) gen in v : randoms gen'
    (cs, ds) = splitAt partitions exponents
    elements = zipWith (\c d -> mulMod (powMod g c p) (powMod h d p) p) cs ds

-- | Which precomputed step to take from @y@: the top five bits of a
-- multiplicative hash, so it does not depend on the distinguishing bits.
partitionOf :: Word -> Int
partitionOf y = fromIntegral ((y * 0x9E3779B97F4A7C15) `shiftR` 59)
{-# INLINE partitionOf #-}

-- | Result of following a walk until it reaches a distinguished point.
data Outcome
  = Distinguished !Point
  | -- | The walk ran too long (it is probably stuck in a cycle).
    Lost
  | Halted

-- | Parallel collision search with distinguished points (van Oorschot and
-- Wiener).
--
-- All workers use the same walk, each starting from its own random points.
-- A point is distinguished when its lowest @t@ bits are zero (about one
-- point in @2^t@). Workers only report distinguished points to the shared
-- table: once two walks meet they continue together, so they reach the same
-- distinguished point, where the collision is noticed. After a
-- distinguished point a worker starts a new walk. The work is divided
-- between the threads and the expected time falls almost linearly with
-- their number.
parallelPollardRho :: Int -> Int -> Problem -> IO (Maybe Word)
parallelPollardRho k seed pr@(Problem p _ _ n)
  | not (hasSolution pr) = pure Nothing
  | n < smallOrder = pure (bruteForce pr)
  | otherwise = do
      table <- newIORef Map.empty
      parallelSearch k $ \w stop -> worker table stop (mkStdGen (seed + 7919 * (w + 1)))
  where
    walk = randomWalk pr (mkStdGen seed)
    -- About 2^8 distinguished points are expected before the collision,
    -- so a collision is noticed soon after it happens.
    t = max 0 (floor (log2 n) `div` 2 - 8) :: Int
    dpMask = (1 `shiftL` t) - 1 :: Word
    maxSteps = 20 * (1 `shiftL` t) :: Int

    worker table stop gen0 = loop gen0
      where
        -- The flag is checked before every walk: walks of small problems
        -- are shorter than the check interval inside 'walkToDistinguished'.
        loop gen = do
          halt <- stopRequested stop
          if halt then pure Nothing else walkFrom gen
        walkFrom gen = do
          let (start, gen') = randomPoint pr gen
          outcome <- walkToDistinguished stop start
          case outcome of
            Halted -> pure Nothing
            Lost -> loop gen'
            Distinguished point@(Point y a b) -> do
              previous <- atomicModifyIORef' table $ \m -> case Map.lookup y m of
                Nothing -> (Map.insert y point m, Nothing)
                Just old -> (m, Just old)
              case previous >>= \(Point _ a' b') -> solveRelation pr a b a' b' of
                Just x -> pure (Just x)
                Nothing -> loop gen'

    walkToDistinguished :: Stop -> Point -> IO Outcome
    walkToDistinguished stop (Point y0 a0 b0)
      -- One copy of the loop per multiplication routine (see 'isSmallModulus').
      | isSmallModulus p = walkWith mulModSmall
      | otherwise = walkWith mulModLarge
      where
        walkWith mul = go 0 y0 a0 b0
          where
            go :: Int -> Word -> Word -> Word -> IO Outcome
            go !steps !y !a !b
              | y .&. dpMask == 0 = pure (Distinguished (Point y a b))
              | steps >= maxSteps = pure Lost
              | steps .&. 0xFFFF == 0xFFFF = do
                  -- Long walks look at the stop flag now and then.
                  halt <- stopRequested stop
                  if halt then pure Halted else next
              | otherwise = next
              where
                s = partitionOf y
                next =
                  go
                    (steps + 1)
                    (mul y (U.unsafeIndex (stepElements walk) s) p)
                    (addMod a (U.unsafeIndex (stepA walk) s) n)
                    (addMod b (U.unsafeIndex (stepB walk) s) n)
        {-# INLINE walkWith #-}
