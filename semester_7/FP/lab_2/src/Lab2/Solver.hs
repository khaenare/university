-- | The three algorithms behind one interface.
module Lab2.Solver
  ( Algorithm (..)
  , allAlgorithms
  , algorithmKey
  , algorithmTitle
  , maxOrderFor
  , solveSequential
  , solveParallel
  ) where

import qualified Lab2.BabyGiant as BabyGiant
import qualified Lab2.BruteForce as BruteForce
import qualified Lab2.PollardRho as PollardRho
import Lab2.Problem (Problem, maxModulus)

data Algorithm = BruteForce | BabyGiant | PollardRho
  deriving (Show, Eq, Enum, Bounded)

allAlgorithms :: [Algorithm]
allAlgorithms = [minBound .. maxBound]

-- | Name used on the command line.
algorithmKey :: Algorithm -> String
algorithmKey BruteForce = "brute"
algorithmKey BabyGiant = "bsgs"
algorithmKey PollardRho = "rho"

algorithmTitle :: Algorithm -> String
algorithmTitle BruteForce = "Brute force"
algorithmTitle BabyGiant = "Baby-step giant-step"
algorithmTitle PollardRho = "Pollard's rho"

-- | Largest order of @g@ the algorithm is run for (time or memory limit).
maxOrderFor :: Algorithm -> Word
maxOrderFor BruteForce = BruteForce.maxOrder
maxOrderFor BabyGiant = BabyGiant.maxOrder
maxOrderFor PollardRho = maxModulus

-- | Single-threaded version. The seed only matters for Pollard's rho.
solveSequential :: Algorithm -> Int -> Problem -> Maybe Word
solveSequential BruteForce _ = BruteForce.bruteForce
solveSequential BabyGiant _ = BabyGiant.babyGiant
solveSequential PollardRho seed = PollardRho.pollardRho seed

-- | Parallel version with the given number of worker threads.
solveParallel :: Algorithm -> Int -> Int -> Problem -> IO (Maybe Word)
solveParallel BruteForce k _ = BruteForce.parallelBruteForce k
solveParallel BabyGiant k _ = BabyGiant.parallelBabyGiant k
solveParallel PollardRho k seed = PollardRho.parallelPollardRho k seed
