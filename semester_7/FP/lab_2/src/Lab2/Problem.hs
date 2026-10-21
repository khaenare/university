-- | The discrete logarithm problem: find @x@ with @g^x ≡ h (mod p)@.
module Lab2.Problem
  ( Problem (..)
  , maxModulus
  , mkProblem
  , randomProblem
  , hasSolution
  , isSolution
  , solveRelation
  ) where

import Data.List (find)
import System.Random (StdGen, uniformR)

import Lab2.Arith (invMod, powMod)
import Lab2.Prime (isPrime, multiplicativeOrder, primitiveRoot, randomSafePrime)

-- | A problem instance. The answer is the unique @x@ in @[0, order)@.
data Problem = Problem
  { modulus :: !Word
  -- ^ prime @p@
  , base :: !Word
  -- ^ @g@
  , target :: !Word
  -- ^ @h@
  , order :: !Word
  -- ^ multiplicative order @n@ of @g@ modulo @p@
  }
  deriving (Show, Eq)

-- | Moduli are kept below 2^62 so that all residue arithmetic fits in 64 bits.
maxModulus :: Word
maxModulus = 2 ^ (62 :: Int)

-- | Check the input and compute the order of @g@.
mkProblem :: Word -> Word -> Word -> Either String Problem
mkProblem p g h
  | p < 3 || p >= maxModulus = Left "p must be a prime between 3 and 2^62"
  | not (isPrime p) = Left ("p = " ++ show p ++ " is not prime")
  | g == 0 || g >= p = Left "g must be between 1 and p - 1"
  | h == 0 || h >= p = Left "h must be between 1 and p - 1"
  | otherwise = Right (Problem p g h (multiplicativeOrder g p))

-- | Random problem with a safe prime of the given size, a generator @g@ and
-- a random exponent. Also returns the exponent used to build @h@.
randomProblem :: Int -> StdGen -> (Problem, Word, StdGen)
randomProblem bits gen0 = (Problem p g (powMod g x p) (p - 1), x, gen2)
  where
    (p, gen1) = randomSafePrime bits gen0
    g = primitiveRoot p
    (x, gen2) = uniformR (0, p - 2) gen1

-- | The multiplicative group modulo a prime is cyclic, so @h@ is a power of
-- @g@ exactly when @h^n ≡ 1@ for the order @n@ of @g@.
hasSolution :: Problem -> Bool
hasSolution pr = powMod (target pr) (order pr) (modulus pr) == 1

isSolution :: Problem -> Word -> Bool
isSolution pr x = x < order pr && powMod (base pr) x (modulus pr) == target pr

-- | Solve a collision @g^a h^b ≡ g^a' h^b'@ for @x@.
--
-- It gives @x (b' - b) ≡ a - a' (mod n)@; with @d = gcd (b' - b, n)@ there
-- are @d@ candidates, and the one that really solves the problem is chosen.
solveRelation :: Problem -> Word -> Word -> Word -> Word -> Maybe Word
solveRelation pr a b a' b'
  | r == 0 || s `mod` d /= 0 || d > maxCandidates = Nothing
  | otherwise = do
      inv <- invMod (r `div` d) n1
      let x0 = (s `div` d) * inv `mod` n1
      find (isSolution pr) [fromInteger (x0 + t * n1) | t <- [0 .. d - 1]]
  where
    n = toInteger (order pr)
    r = (toInteger b' - toInteger b) `mod` n
    s = (toInteger a - toInteger a') `mod` n
    d = gcd r n
    n1 = n `div` d
    maxCandidates = 2 ^ (16 :: Int)
