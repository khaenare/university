module Main (main) where

import Control.Concurrent (getNumCapabilities)
import Control.Monad (forM, when)
import Data.List (nub, sort)
import Data.Maybe (fromMaybe)
import GHC.Conc (getNumProcessors)
import Options.Applicative
import System.Exit (exitFailure)
import System.IO (hPutStrLn, stderr)
import System.Random (mkStdGen, randomRIO)
import Text.Printf (printf)
import Text.Read (readMaybe)

import Lab2.Arith (log2)
import Lab2.Bench (benchmark, renderBench, timed)
import Lab2.Parallel (maxWorkers)
import Lab2.Problem (Problem (..), hasSolution, isSolution, mkProblem, randomProblem)
import Lab2.Solver
import Lab2.Table (renderTable)

-- Command line -----------------------------------------------------------------

-- | Where the problem comes from.
data Source
  = Given Word Word Word
  | -- | Random problem of the given size.
    Generated Int

data Command
  = -- | Problem, algorithms, threads and the seed of the random problem
    -- and of the random walks.
    Solve Source [Algorithm] (Maybe Int) (Maybe Int)
  | Generate Int (Maybe Int)
  | Bench Algorithm Int (Maybe [Int]) Int Int

commandParser :: Parser Command
commandParser =
  hsubparser
    ( command "solve" (info solveParser (progDesc "Solve a problem with the sequential and parallel algorithms"))
        <> command "generate" (info generateParser (progDesc "Print a random problem with a known answer"))
        <> command "bench" (info benchParser (progDesc "Measure the speedup for different numbers of threads"))
    )
  where
    solveParser =
      Solve <$> sourceParser <*> many algorithmOption <*> optional threadsOption <*> optional seedOption
    generateParser = Generate <$> bitsOption <*> optional seedOption
    benchParser =
      Bench
        <$> algorithmOption
        <*> bitsOption
        <*> optional (option threadListReader (long "threads" <> short 't' <> metavar "LIST"
              <> help "Thread counts, e.g. 1,2,4,8 (default: powers of two and all cores)"))
        <*> option positiveReader (long "runs" <> short 'r' <> metavar "N" <> value 3 <> showDefault
              <> help "Runs of every configuration; the mean is reported")
        <*> option auto (long "seed" <> short 's' <> metavar "SEED" <> value 2026 <> showDefault
              <> help "Seed of the random problem")

    sourceParser = given <|> (Generated <$> bitsOption)
    given =
      Given
        <$> option wordReader (long "modulus" <> short 'p' <> metavar "P" <> help "Prime modulus p")
        <*> option wordReader (long "base" <> short 'g' <> metavar "G" <> help "Base g")
        <*> option wordReader (long "target" <> short 'y' <> metavar "H" <> help "Value h, find x with g^x = h (mod p)")
    bitsOption =
      option bitsReader (long "bits" <> short 'b' <> metavar "BITS" <> help "Size of a random prime p, 8..62 bits")
    seedOption =
      option auto (long "seed" <> short 's' <> metavar "SEED" <> help "Seed of the random problem and of the random walks")
    threadsOption =
      option threadsReader (long "threads" <> short 't' <> metavar "K" <> help "Worker threads (default: all cores)")
    algorithmOption =
      option algorithmReader (long "algorithm" <> short 'a' <> metavar "brute|bsgs|rho"
        <> help "Algorithm; may be repeated (default for solve: all)")

-- | Non-negative integer that fits into a 'Word' (no silent wrap-around).
wordReader :: ReadM Word
wordReader = eitherReader $ \s -> case readMaybe s :: Maybe Integer of
  Just n | n >= 0 && n <= toInteger (maxBound :: Word) -> Right (fromInteger n)
  _ -> Left ("expected a non-negative integer below 2^64, got " ++ show s)

bitsReader :: ReadM Int
bitsReader = eitherReader $ \s -> case readMaybe s of
  Just b | b >= 8 && b <= 62 -> Right b
  _ -> Left "the size must be from 8 to 62 bits"

positiveReader :: ReadM Int
positiveReader = eitherReader $ \s -> case readMaybe s of
  Just n | n >= 1 -> Right n
  _ -> Left ("expected a positive integer, got " ++ show s)

validThreads :: Int -> Bool
validThreads k = k >= 1 && k <= maxWorkers

threadsReader :: ReadM Int
threadsReader = eitherReader $ \s -> case readMaybe s of
  Just k | validThreads k -> Right k
  _ -> Left ("the number of threads must be from 1 to " ++ show maxWorkers)

threadListReader :: ReadM [Int]
threadListReader = eitherReader $ \s ->
  case mapM readMaybe (splitOn ',' s) of
    Just ks@(_ : _) | all validThreads ks -> Right ks
    _ -> Left ("expected thread counts from 1 to " ++ show maxWorkers ++ " separated by commas, e.g. 1,2,4,8")
  where
    splitOn c text = case break (== c) text of
      (a, []) -> [a]
      (a, _ : rest) -> a : splitOn c rest

algorithmReader :: ReadM Algorithm
algorithmReader = eitherReader $ \s ->
  maybe (Left ("unknown algorithm " ++ show s ++ ", use brute, bsgs or rho")) Right
    (lookup s [(algorithmKey a, a) | a <- allAlgorithms])

main :: IO ()
main = do
  cmd <- execParser (info (commandParser <**> helper)
    (fullDesc <> progDesc "Parallel discrete logarithm: find x with g^x = h (mod p)"))
  case cmd of
    Solve source algorithms threads seed -> runSolve source algorithms threads seed
    Generate bits seed -> runGenerate bits seed
    Bench algorithm bits threads runs seed -> runBench algorithm bits threads runs seed

-- Commands -------------------------------------------------------------------

failWith :: String -> IO a
failWith message = hPutStrLn stderr ("Error: " ++ message) >> exitFailure

newSeed :: IO Int
newSeed = randomRIO (1, 999999)

describe :: Problem -> IO ()
describe pr = do
  printf "p = %d, g = %d, h = %d\n" (modulus pr) (base pr) (target pr)
  printf "Order of g: n = %d (about 2^%.1f)\n" (order pr) (log2 (order pr))

describeMachine :: Int -> IO ()
describeMachine k = do
  caps <- getNumCapabilities
  cores <- getNumProcessors
  printf "Worker threads: %d; runtime capabilities (+RTS -N): %d; CPU cores: %d\n" k caps cores
  when (k > caps) $
    putStrLn "Note: more threads than capabilities, some of them will share a core."

runSolve :: Source -> [Algorithm] -> Maybe Int -> Maybe Int -> IO ()
runSolve source algorithms threads given = do
  seed <- maybe newSeed pure given
  pr <- case source of
    Given p g h -> either failWith pure (mkProblem p g h)
    Generated bits -> do
      putStrLn "Random problem"
      pure (let (pr, _, _) = randomProblem bits (mkStdGen seed) in pr)
  -- Printed so that a run (including Pollard's random walks) can be repeated.
  printf "Seed: %d\n" seed
  k <- maybe (min maxWorkers <$> getNumCapabilities) pure threads
  describe pr
  describeMachine k
  putStrLn ""
  let chosen = if null algorithms then allAlgorithms else nub algorithms
  results <- forM chosen $ \algorithm -> do
    let title = algorithmTitle algorithm
    if order pr > maxOrderFor algorithm
      then
        pure
          ( [[title, "-", "-", printf "skipped: order above 2^%.0f" (log2 (maxOrderFor algorithm)), "-"]]
          , [] )
      else do
        (xs, ts) <- timed (pure (solveSequential algorithm seed pr))
        (xp, tp) <- timed (solveParallel algorithm k seed pr)
        pure
          ( [ [title, "sequential", "1", showResult xs, printf "%.3f" ts]
            , [title, "parallel", show k, showResult xp, printf "%.3f" tp]
            ]
          , [xs, xp] )
  mapM_ putStrLn (renderTable ["Algorithm", "Version", "Threads", "x", "Time, s"] (concatMap fst results))
  putStrLn ""
  -- The answer in [0, n) is unique, so every algorithm must return the same.
  case nub (concatMap snd results) of
    [] -> pure ()
    [Just x] | isSolution pr x ->
      printf "Check passed: %d^%d mod %d = %d\n" (base pr) x (modulus pr) (target pr)
    [Nothing] | not (hasSolution pr) -> putStrLn "No solution: h is not a power of g modulo p."
    answers -> failWith ("wrong or different results: " ++ show answers)
  where
    showResult = maybe "no solution" show

runGenerate :: Int -> Maybe Int -> IO ()
runGenerate bits given = do
  seed <- maybe newSeed pure given
  let (pr, x, _) = randomProblem bits (mkStdGen seed)
  printf "Random problem, seed %d\n" seed
  describe pr
  printf "Answer: x = %d\n" x
  printf "Solve it with: lab2 solve -p %d -g %d -y %d\n" (modulus pr) (base pr) (target pr)

runBench :: Algorithm -> Int -> Maybe [Int] -> Int -> Int -> IO ()
runBench algorithm bits threads runs seed = do
  caps <- getNumCapabilities
  let (pr, _, _) = randomProblem bits (mkStdGen seed)
      counts = fromMaybe (defaultCounts caps) threads
  when (order pr > maxOrderFor algorithm) $
    failWith (printf "%s is limited to orders below 2^%.0f, use fewer bits"
      (algorithmTitle algorithm) (log2 (maxOrderFor algorithm)))
  printf "%s, %d-bit problem (seed %d), %d run(s) per configuration\n" (algorithmTitle algorithm) bits seed runs
  describe pr
  describeMachine (maximum counts)
  putStrLn ""
  rows <- benchmark algorithm pr counts runs seed
  mapM_ putStrLn (renderBench rows)
  where
    defaultCounts caps =
      let top = min maxWorkers caps
       in sort (nub (takeWhile (<= top) (iterate (* 2) 1) ++ [top]))
