-- | Property tests of the arithmetic and of all solvers.
module Main (main) where

import Control.Monad (forM, unless)
import Data.Maybe (listToMaybe)
import System.Exit (exitFailure)
import System.Random (mkStdGen)
import Test.QuickCheck
import Test.QuickCheck.Monadic (assert, monadicIO, run)

import Lab2.Arith (ceilSqrt, mulMod, powMod)
import Lab2.Prime (factorize, isPrime, multiplicativeOrder, primitiveRoot)
import Lab2.Problem
import Lab2.Solver

-- | A modulus from 2 up to 2^62, with small and large sizes equally likely
-- (to cover both branches of 'mulMod').
newtype Modulus = Modulus Word
  deriving (Show)

instance Arbitrary Modulus where
  arbitrary = do
    bits <- chooseInt (2, 62)
    Modulus <$> choose (2, 2 ^ bits)

prop_mulMod :: Modulus -> Word -> Word -> Bool
prop_mulMod (Modulus m) a b =
  toInteger (mulMod (a `rem` m) (b `rem` m) m) == toInteger a * toInteger b `mod` toInteger m

prop_powMod :: Modulus -> Word -> Small Word -> Bool
prop_powMod (Modulus m) b (Small e) =
  toInteger (powMod b e m) == (toInteger b ^ e) `mod` toInteger m

prop_ceilSqrt :: Word -> Bool
prop_ceilSqrt x = r * r >= n && (r == 0 || (r - 1) * (r - 1) < n)
  where
    n = x `rem` (2 ^ (62 :: Int))
    r = ceilSqrt n

prop_isPrimeSmall :: Property
prop_isPrimeSmall = forAll (choose (0, 100000)) $ \n -> isPrime n == naive n
  where
    naive n = n >= 2 && all (\d -> n `rem` d /= 0) (takeWhile (\d -> d * d <= n) [2 ..])

-- | Known primes and composites, including Carmichael numbers and
-- strong pseudoprimes to small bases.
prop_isPrimeKnown :: Property
prop_isPrimeKnown =
  conjoin
    [ counterexample (show n) (isPrime n === expected)
    | (n, expected) <-
        [ (2 ^ (61 :: Int) - 1, True)
        , (4611686018427387847, True)
        , (561, False)
        , (3215031751, False)
        , (3825123056546413051, False)
        , (2 ^ (31 :: Int) - 1, True)
        , (1000000007 * 998244353, False)
        ]
    ]

prop_factorize :: Modulus -> Property
prop_factorize (Modulus m) =
  product [q ^ e | (q, e) <- fs] === m .&&. all (isPrime . fst) fs
  where
    fs = factorize m

prop_order :: Property
prop_order = forAll smallPrime $ \p -> forAll (choose (1, p - 1)) $ \g ->
  let n = multiplicativeOrder g p
   in powMod g n p == 1 && all (\(q, _) -> powMod g (n `quot` q) p /= 1) (factorize n)

prop_primitiveRoot :: Property
prop_primitiveRoot = forAll smallPrime $ \p -> multiplicativeOrder (primitiveRoot p) p === p - 1

smallPrime :: Gen Word
smallPrime = choose (3, 2 ^ (40 :: Int)) `suchThat` isPrime

-- | Every solver, sequential and parallel (1..4 threads), on a problem.
allSolvers :: Problem -> Int -> IO [(String, Maybe Word)]
allSolvers = solvers allAlgorithms

-- | The given algorithms, sequential and parallel (1..4 threads).
solvers :: [Algorithm] -> Problem -> Int -> IO [(String, Maybe Word)]
solvers algorithms pr seed = fmap concat $ forM algorithms $ \a ->
  if order pr > maxOrderFor a
    then pure []
    else do
      parallel <- forM [1 .. 4] $ \k -> (,) (algorithmKey a ++ " x" ++ show k) <$> solveParallel a k seed pr
      pure ((algorithmKey a ++ " seq", solveSequential a seed pr) : parallel)

-- | Random problems with a generator: all solvers find the hidden exponent.
prop_solvesRandom :: Property
prop_solvesRandom = forAll (chooseInt (8, 26)) $ \bits -> forAll arbitrary $ \seed ->
  let (pr, x, _) = randomProblem bits (mkStdGen seed)
   in monadicIO $ do
        results <- run (allSolvers pr seed)
        unless (all ((== Just x) . snd) results) $ run (print (pr, x, results))
        assert (all ((== Just x) . snd) results)

-- | Any base, including ones of small order: the answer is the unique
-- solution below the order, or none.
prop_solvesAnyBase :: Property
prop_solvesAnyBase = forAll tinyPrime $ \p -> forAll (choose (1, p - 1)) $ \g ->
  forAll (choose (1, p - 1)) $ \h -> forAll arbitrary $ \seed ->
    case mkProblem p g h of
      Left err -> counterexample err False
      Right pr -> monadicIO $ do
        results <- run (allSolvers pr seed)
        let expected = if hasSolution pr then filter (isSolution pr) [0 .. order pr - 1] else []
        assert (all ((== listToMaybe expected) . snd) results)
  where
    tinyPrime = choose (3, 2 ^ (14 :: Int)) `suchThat` isPrime

-- | Bases that are not generators, with orders above 2^17 so that Pollard's
-- rho really walks (smaller groups go to exhaustive search): @g = r^k@ for
-- a primitive root @r@ and a divisor @k@ of @p - 1@, so @g@ has order
-- @(p - 1) / k@ and collisions often have @gcd (b' - b, n) > 1@. In half of
-- the cases @h = r@, which lies outside the subgroup of @g@ when @k > 1@.
prop_nonGenerators :: Property
prop_nonGenerators =
  forAll (choose (2 ^ (20 :: Int), 2 ^ (32 :: Int)) `suchThat` isPrime) $ \p ->
    forAll (divisorFor p) $ \k ->
      let r = primitiveRoot p
          g = powMod r k p
          n = (p - 1) `quot` k
       in forAll (choose (0, n - 1)) $ \x -> forAll arbitrary $ \inGroup -> forAll arbitrary $ \seed ->
            let solvable = inGroup || k == 1
                h = if solvable then powMod g x p else r
             in case mkProblem p g h of
                  Left err -> counterexample err False
                  Right pr -> monadicIO $ do
                    results <- run (solvers [BabyGiant, PollardRho] pr seed)
                    let expected = if solvable then Just x else Nothing
                    unless (order pr == n && all ((== expected) . snd) results) $
                      run (print (pr, expected, results))
                    assert (order pr == n && all ((== expected) . snd) results)
  where
    -- A product of some prime factors of p - 1 that leaves an order >= 2^17.
    divisorFor p =
      (product <$> sublistOf [q | (q, e) <- factorize (p - 1), _ <- [1 .. e]])
        `suchThat` (\k -> (p - 1) `quot` k >= 2 ^ (17 :: Int))

-- | A larger problem for the square-root algorithms only.
prop_solvesLarge :: Property
prop_solvesLarge = once $ forAll arbitrary $ \seed ->
  let (pr, x, _) = randomProblem 44 (mkStdGen seed)
   in monadicIO $ do
        results <- run (allSolvers pr seed)
        assert (not (null results) && all ((== Just x) . snd) results)

main :: IO ()
main = do
  results <-
    sequence
      [ check "mulMod agrees with Integer" 2000 prop_mulMod
      , check "powMod agrees with Integer" 2000 prop_powMod
      , check "ceilSqrt" 2000 prop_ceilSqrt
      , check "isPrime agrees with trial division" 2000 prop_isPrimeSmall
      , check "isPrime on known numbers" 1 prop_isPrimeKnown
      , check "factorize" 500 prop_factorize
      , check "multiplicativeOrder" 300 prop_order
      , check "primitiveRoot" 200 prop_primitiveRoot
      , check "solvers on random problems" 60 prop_solvesRandom
      , check "solvers with any base" 200 prop_solvesAnyBase
      , check "bsgs and rho with non-generator bases" 150 prop_nonGenerators
      , check "solvers on a 44-bit problem" 1 prop_solvesLarge
      ]
  unless (and results) exitFailure
  where
    check :: Testable prop => String -> Int -> prop -> IO Bool
    check name n prop = do
      putStrLn ("--- " ++ name)
      isSuccess <$> quickCheckWithResult stdArgs {maxSuccess = n} prop
