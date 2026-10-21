-- | Time measurements of the solvers.
module Lab2.Bench
  ( timed
  , BenchRow (..)
  , benchmark
  , renderBench
  ) where

import Control.Exception (evaluate, throwIO)
import Control.Monad (forM, unless)
import GHC.Clock (getMonotonicTime)
import System.Mem (performMajorGC)
import Text.Printf (printf)

import Lab2.Problem (Problem, hasSolution, isSolution)
import Lab2.Solver (Algorithm, algorithmTitle, solveParallel, solveSequential)
import Lab2.Table (renderTable)

-- | Run a solver, force its result and return the wall-clock time in seconds.
timed :: IO (Maybe Word) -> IO (Maybe Word, Double)
timed solve = do
  start <- getMonotonicTime
  result <- solve >>= evaluate
  mapM_ evaluate result
  end <- getMonotonicTime
  pure (result, end - start)

data BenchRow = BenchRow
  { rowParallel :: Bool
  , rowThreads :: Int
  , rowTimes :: [Double]
  }

-- | Measure the sequential version and the parallel one for every thread
-- count, @runs@ times each (run @r@ uses seed @seed + r@). Every result is
-- checked, so a wrong answer stops the benchmark.
benchmark :: Algorithm -> Problem -> [Int] -> Int -> Int -> IO [BenchRow]
benchmark algorithm pr threadCounts runs seed = do
  sequentialRow <- measure False 1 (\s -> pure (solveSequential algorithm s pr))
  parallelRows <- forM threadCounts $ \k -> measure True k (\s -> solveParallel algorithm k s pr)
  pure (sequentialRow : parallelRows)
  where
    measure parallel k solve = do
      times <- forM [1 .. runs] $ \r -> do
        -- Collect the garbage of the previous run now, not inside this one.
        performMajorGC
        (result, seconds) <- timed (solve (seed + r))
        unless (maybe (not (hasSolution pr)) (isSolution pr) result) $
          throwIO (userError (algorithmTitle algorithm ++ " returned a wrong result"))
        pure seconds
      pure (BenchRow parallel k times)

-- | Markdown table: mean and minimum time, speedup against the parallel
-- version on one thread and against the sequential version, and
-- efficiency (speedup on one thread basis divided by the thread count).
renderBench :: [BenchRow] -> [String]
renderBench rows =
  renderTable
    ["Version", "Threads", "Mean, s", "Min, s", "Speedup vs 1 thread", "Speedup vs sequential", "Efficiency"]
    (map row rows)
  where
    mean xs = sum xs / fromIntegral (length xs)
    sequentialMean = mean (concat [rowTimes r | r <- rows, not (rowParallel r)])
    oneThreadMean = case [rowTimes r | r <- rows, rowParallel r, rowThreads r == 1] of
      times : _ -> Just (mean times)
      [] -> Nothing
    fixed :: Int -> Double -> String
    fixed digits = printf ("%." ++ show digits ++ "f")
    row r
      | not (rowParallel r) =
          ["sequential", "1", fixed 3 m, fixed 3 (minimum (rowTimes r)), "-", "1.00", "-"]
      | otherwise =
          [ "parallel"
          , show (rowThreads r)
          , fixed 3 m
          , fixed 3 (minimum (rowTimes r))
          , maybe "-" (\t1 -> fixed 2 (t1 / m)) oneThreadMean
          , fixed 2 (sequentialMean / m)
          , maybe "-" (\t1 -> fixed 2 (t1 / m / fromIntegral (rowThreads r))) oneThreadMean
          ]
      where
        m = mean (rowTimes r)
