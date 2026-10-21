-- | Alphabetical order of words.
--
-- Unicode code points do not follow the Ukrainian alphabet (Ґ, Є, І and Ї
-- lie outside the range А..Я), so letters are compared by their place in
-- explicit alphabets: digits first, then Latin, then Cyrillic, then any
-- other letters by code point.
module Lab3.Alphabet
  ( Rank
  , rank
  , primaryLetter
  , sortKey
  , firstLetter
  , compareWords
  , cyrillicAlphabet
  ) where

import Prelude hiding (Word)

import Data.Char (isAlphaNum, isAscii, isAsciiLower, isDigit, isLetter, ord, toLower)
import qualified Data.Map.Strict as Map
import Data.Ord (comparing)
import qualified Data.Text as T
import Data.Text.Normalize (NormalizationMode (NFD), normalize)

import Lab3.Parse (isApostrophe)
import Lab3.Types (Word, wordString)

-- | Position of a letter: (alphabet, place in it).
type Rank = (Int, Int)

-- | Ukrainian alphabet with the letters of Russian added where Russian
-- dictionaries put them (ё after е, ъ ы э before ю).
cyrillicAlphabet :: String
cyrillicAlphabet = "абвгґдеёєжзиіїйклмнопрстуфхцчшщъыьэюя"

cyrillicRanks :: Map.Map Char Int
cyrillicRanks = Map.fromList (zip cyrillicAlphabet [0 ..])

-- | A letter in lower case; Latin letters with diacritics become their base
-- letter (é → e, ü → u, ł stays ł), as in dictionaries. Cyrillic letters
-- are kept as they are: й, ї, ё are letters of their own.
primaryLetter :: Char -> Char
primaryLetter c
  | isAscii l || Map.member l cyrillicRanks = l
  | otherwise = case T.unpack (normalize NFD (T.singleton l)) of
      base : _ | isAsciiLower base -> base
      _ -> l
  where
    l = toLower c

-- | Rank of a letter or digit.
rank :: Char -> Rank
rank c
  | isDigit l = (0, ord l)
  | isAsciiLower l = (1, ord l)
  | Just i <- Map.lookup l cyrillicRanks = (2, i)
  | otherwise = (3, ord l)
  where
    l = primaryLetter c

-- | Letters and digits of a word ('ʼ' counts as a letter in Unicode, but
-- here it is an apostrophe).
significant :: Word -> String
significant = filter (\c -> isAlphaNum c && not (isApostrophe c)) . wordString

-- | The first letter of a word as used for grouping: digits before it are
-- skipped ("64-бітний" belongs to б), and it is in lower case without
-- Latin diacritics.
firstLetter :: Word -> Char
firstLetter w = case filter isLetter (significant w) of
  c : _ -> primaryLetter c
  [] -> ' ' -- not reached: a word always contains a letter

-- | What words are sorted by: the first letter, then all their letters and
-- digits. Case, apostrophes, hyphens and underscores are ignored, as in
-- dictionaries (пам'ять is sorted as память).
sortKey :: Word -> [Rank]
sortKey w = rank (firstLetter w) : map rank (significant w)

-- | Alphabetical order; words with the same key are ordered by their
-- spelling, so the order is always the same.
compareWords :: Word -> Word -> Ordering
compareWords = comparing sortKey <> comparing wordString
