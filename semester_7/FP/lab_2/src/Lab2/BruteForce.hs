-- | Exhaustive search: try @x = 0, 1, 2, ...@ until @g^x ≡ h@.
--
-- Needs @O(n)@ multiplications for the order @n@ of @g@, so it is only
-- practical for small groups, but it parallelises perfectly.
module Lab2.BruteForce
  ( maxOrder
  , bruteForce
  , parallelBruteForce
  ) where

import Lab2.Parallel (BlockScan, geometricScan, parallelGeometricScan, scanRange)
import Lab2.Problem (Problem (..))

-- | Largest group order accepted by the command line. Above 2^32 every
-- step needs the 128-bit multiplication (about 12 ns), so 2^34 steps take up
-- to about 3.5 minutes on one thread.
maxOrder :: Word
maxOrder = 2 ^ (34 :: Int)

-- | Sequential exhaustive search. The sequence is @y_x = g^x@, so the
-- index of @h@ in it is the answer.
bruteForce :: Problem -> Maybe Word
bruteForce pr = fst <$> geometricScan 1 (order pr) (scanPowers pr)

-- | Exhaustive search with @k@ worker threads.
parallelBruteForce :: Int -> Problem -> IO (Maybe Word)
parallelBruteForce k pr@(Problem p g _ n) = fmap fst <$> parallelGeometricScan k p 1 g n (scanPowers pr)

-- | Look for @h@ among consecutive powers of @g@.
scanPowers :: Problem -> BlockScan
scanPowers (Problem p g h _) = scanRange p g (== h)
{-# NOINLINE scanPowers #-}
