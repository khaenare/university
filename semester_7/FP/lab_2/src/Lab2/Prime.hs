-- | Primality, factorisation and multiplicative orders for 64-bit numbers
-- (all numbers must be below 2^63, see "Lab2.Arith").
module Lab2.Prime
  ( isPrime
  , factorize
  , multiplicativeOrder
  , primitiveRoot
  , randomSafePrime
  ) where

import Data.List (sort)
import qualified Data.List.NonEmpty as NE
import Data.Maybe (fromMaybe)
import System.Random (StdGen, uniformR)

import Lab2.Arith (addMod, mulMod, powMod)

-- | Deterministic Miller–Rabin test; these bases are enough for every
-- number below 3.3 * 10^24.
isPrime :: Word -> Bool
isPrime n
  | n < 2 = False
  | n `elem` witnesses = True
  | any (\q -> n `rem` q == 0) witnesses = False
  | otherwise = all (strongProbablePrime n) witnesses
  where
    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]

-- | Miller–Rabin round for an odd @n@ and base @a@.
strongProbablePrime :: Word -> Word -> Bool
strongProbablePrime n a = x == 1 || go (s - 1) x
  where
    (s, d) = splitPowerOfTwo (n - 1)
    x = powMod a d n
    -- Look for n - 1 among x, x^2, ..., x^(2^(s-1)).
    go :: Int -> Word -> Bool
    go k y
      | y == n - 1 = True
      | k <= 0 = False
      | otherwise = go (k - 1) (mulMod y y n)

-- | @(s, d)@ with @m = 2^s * d@ and @d@ odd, for @m > 0@.
splitPowerOfTwo :: Word -> (Int, Word)
splitPowerOfTwo = go 0
  where
    go s d
      | even d = go (s + 1) (d `quot` 2)
      | otherwise = (s, d)

-- | Prime factorisation as @(prime, exponent)@ pairs in increasing order.
factorize :: Word -> [(Word, Int)]
factorize n0
  | n0 <= 1 = []
  | otherwise = map (\ps -> (NE.head ps, length ps)) (NE.group (sort (trial n0 2)))
  where
    -- Trial division removes the small factors quickly.
    trial n d
      | n == 1 = []
      | d > 1000 = split n
      | n `rem` d == 0 = d : trial (n `quot` d) d
      | otherwise = trial n (if d == 2 then 3 else d + 2)
    split n
      | n == 1 = []
      | isPrime n = [n]
      | otherwise = let d = findDivisor n in split d ++ split (n `quot` d)

-- | A non-trivial divisor of a composite @n@ (Pollard's rho method).
findDivisor :: Word -> Word
findDivisor n = go 1
  where
    go c = fromMaybe (go (c + 1)) (attempt c)
    attempt c = loop 2 2
      where
        f x = addMod (mulMod x x n) c n
        loop x y =
          let x' = f x
              y' = f (f y)
              d = gcd (if x' > y' then x' - y' else y' - x') n
           in if d == 1 then loop x' y' else if d == n then Nothing else Just d

-- | Order of @g@ in the multiplicative group modulo a prime @p@.
multiplicativeOrder :: Word -> Word -> Word
multiplicativeOrder g p = foldl' reduce (p - 1) (factorize (p - 1))
  where
    -- Remove the factor q while g^(m/q) is still 1.
    reduce m (q, e) = go m e
      where
        go k 0 = k
        go k r = if powMod g (k `quot` q) p == 1 then go (k `quot` q) (r - 1 :: Int) else k

-- | Smallest generator of the multiplicative group modulo a prime @p@.
primitiveRoot :: Word -> Word
primitiveRoot 2 = 1
primitiveRoot p = go 2
  where
    primes = map fst (factorize (p - 1))
    go g
      | all (\q -> powMod g ((p - 1) `quot` q) p /= 1) primes = g
      | otherwise = go (g + 1)

-- | Random safe prime @p = 2q + 1@ (with @q@ prime) of exactly @bits@ bits,
-- for @3 <= bits <= 62@. The group order @p - 1 = 2q@ then has a large
-- prime factor, which makes the discrete logarithm hard.
randomSafePrime :: Int -> StdGen -> (Word, StdGen)
randomSafePrime bits gen0 = go gen0
  where
    lo = 2 ^ (bits - 2)
    hi = 2 ^ (bits - 1) - 1
    go gen =
      let (q, gen') = uniformR (lo, hi) gen
          p = 2 * q + 1
       in if odd q && isPrime q && isPrime p then (p, gen') else go gen'
