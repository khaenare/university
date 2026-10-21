{-# LANGUAGE MagicHash #-}
{-# LANGUAGE UnboxedTuples #-}

-- | Modular arithmetic on 64-bit machine words.
--
-- All functions expect a modulus below 2^63 and arguments already reduced
-- modulo it, so sums of two residues never overflow a 'Word'.
module Lab2.Arith
  ( mulMod
  , isSmallModulus
  , mulModSmall
  , mulModLarge
  , addMod
  , powMod
  , invMod
  , ceilSqrt
  , log2
  ) where

import GHC.Exts (Word (..), quotRemWord2#, timesWord2#)

-- | @a * b mod m@ for @a, b < m@.
--
-- When the product fits into 64 bits a plain division is used; otherwise
-- the full 128-bit product is divided with GHC primitives.
mulMod :: Word -> Word -> Word -> Word
mulMod a b m
  | isSmallModulus m = mulModSmall a b m
  | otherwise = mulModLarge a b m
{-# INLINE mulMod #-}

-- | Moduli below 2^32: the product of two residues fits into 64 bits.
--
-- Hot loops test this once and then use 'mulModSmall' or 'mulModLarge'
-- directly instead of 'mulMod', which tests it on every call.
isSmallModulus :: Word -> Bool
isSmallModulus m = m <= 0xFFFFFFFF
{-# INLINE isSmallModulus #-}

mulModSmall :: Word -> Word -> Word -> Word
mulModSmall a b m = a * b `rem` m
{-# INLINE mulModSmall #-}

mulModLarge :: Word -> Word -> Word -> Word
mulModLarge (W# a) (W# b) (W# m) =
  case timesWord2# a b of
    -- hi < m because a, b < m, as quotRemWord2# requires.
    (# hi, lo #) -> case quotRemWord2# hi lo m of
      (# _, r #) -> W# r
{-# INLINE mulModLarge #-}

-- | @a + b mod m@ for @a, b < m@.
addMod :: Word -> Word -> Word -> Word
addMod a b m = let s = a + b in if s >= m then s - m else s
{-# INLINE addMod #-}

-- | @b ^ e mod m@ by binary exponentiation.
powMod :: Word -> Word -> Word -> Word
powMod b0 e0 m = go (b0 `rem` m) e0 (1 `rem` m)
  where
    go _ 0 acc = acc
    go b e acc =
      let acc' = if odd e then mulMod acc b m else acc
       in go (mulMod b b m) (e `quot` 2) acc'

-- | Inverse of @a@ modulo @m@, if @gcd a m == 1@.
invMod :: Integer -> Integer -> Maybe Integer
invMod a m
  | g == 1 = Just (x `mod` m)
  | otherwise = Nothing
  where
    (g, x) = extendedGcd (a `mod` m) m

-- | @(gcd a b, x)@ such that @a * x ≡ gcd a b (mod b)@.
extendedGcd :: Integer -> Integer -> (Integer, Integer)
extendedGcd a b = go a b 1 0
  where
    go r0 r1 s0 s1
      | r1 == 0 = (r0, s0)
      | otherwise =
          let q = r0 `quot` r1
           in go r1 (r0 - q * r1) s1 (s0 - q * s1)

-- | Smallest @r@ with @r * r >= n@.
ceilSqrt :: Word -> Word
ceilSqrt n = up (down (floor (sqrt (fromIntegral n :: Double))))
  where
    -- The floating point estimate can be off by one in either direction.
    down r = if r > 0 && (r - 1) * (r - 1) >= n then down (r - 1) else r
    up r = if r * r >= n then r else up (r + 1)

-- | Binary logarithm, for messages about problem sizes.
log2 :: Word -> Double
log2 n = logBase 2 (fromIntegral n)
