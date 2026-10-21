-- | Variant 6: print the words of the text in alphabetical order by the
-- first letter, starting the words with every new letter from a new
-- indented line ("червоний рядок").
module Lab3.Task
  ( LetterGroup (..)
  , groupByFirstLetter
  , distinctWords
  , layoutGroup
  , layoutGroups
  , displayWidth
  , Statistics (..)
  , statistics
  ) where

import Prelude hiding (Word)

import Data.Char (GeneralCategory (Format), generalCategory, isMark, isUpper, ord, toLower)
import Data.Function (on)
import Data.List (sortOn)
import qualified Data.List.NonEmpty as NE
import qualified Data.Map.Strict as Map
import qualified Data.Set as Set
import Data.Text (Text)
import qualified Data.Text as T

import Lab3.Alphabet (firstLetter, sortKey)
import Lab3.Parse (isApostrophe)
import Lab3.Types

-- | Words of the text that start with the same letter, in alphabetical order.
data LetterGroup = LetterGroup
  { groupLetter :: Char
  , groupWords :: [Word]
  }
  deriving (Show, Eq)

-- | Group the words of the text by their first letter. With @keepRepeats@
-- every occurrence is listed, otherwise each word once ('distinctWords').
groupByFirstLetter :: Bool -> Document -> [LetterGroup]
groupByFirstLetter keepRepeats document =
  [ LetterGroup (firstLetter (NE.head ws)) (NE.toList ws)
  | ws <- NE.groupBy ((==) `on` firstLetter) (sortOn key chosen)
  ]
  where
    all' = wordsOf document
    chosen = if keepRepeats then all' else distinctWords all'
    -- The same order as 'Lab3.Alphabet.compareWords'; 'sortOn' computes the
    -- key of every word only once.
    key w = (sortKey w, wordString w)

-- | Each word once, in the order of first occurrence. Spellings that differ
-- only in case or in the kind of apostrophe or hyphen are the same word; the one with
-- the fewest capital letters is kept ("програма" rather than "Програма" at
-- the start of a sentence, but "Haskell" stays as it is), the first such
-- occurrence if there are several.
distinctWords :: [Word] -> [Word]
distinctWords ws = [snd (best Map.! key) | key <- nubOrd (map identity ws)]
  where
    best = Map.fromListWith keepBetter [(identity w, (rankOf i w, w)) | (i, w) <- zip [0 :: Int ..] ws]
    keepBetter new old = if fst new < fst old then new else old
    nubOrd = go mempty
      where
        go _ [] = []
        go seen (k : rest)
          | k `Set.member` seen = go seen rest
          | otherwise = k : go (Set.insert k seen) rest
    -- Fewer capitals first, then earlier occurrence.
    rankOf i w = (length (filter isUpper (wordString w)), i)
    identity = map (normalize . toLower) . wordString
    normalize c
      | isApostrophe c = '\''
      | c == '\x2010' = '-'
      | otherwise = c

-- | One group as a paragraph of at most @width@ columns per line whose
-- first line starts with @indent@ spaces (the red line). Words are
-- separated by single spaces; a word longer than a line gets a line of its
-- own.
layoutGroup :: Int -> Int -> [Text] -> [Text]
layoutGroup width indent = go (T.replicate indent " ")
  where
    go _ [] = []
    go prefix (w : rest) = fill (prefix <> w) (displayWidth prefix + displayWidth w) rest
    -- The width of the current line is kept, not recomputed for every word.
    fill line _ [] = [line]
    fill line used (w : rest)
      | used + 1 + wordWidth <= width = fill (line <> " " <> w) (used + 1 + wordWidth) rest
      | otherwise = line : go "" (w : rest)
      where
        wordWidth = displayWidth w

-- | Number of terminal columns a text takes: combining marks and format
-- characters take none, wide (East Asian) characters and emoji take two.
displayWidth :: Text -> Int
displayWidth = T.foldl' (\n c -> n + charWidth c) 0
  where
    charWidth c
      | isMark c || generalCategory c == Format = 0
      | isWide (ord c) = 2
      | otherwise = 1
    isWide n =
      any
        (\(lo, hi) -> n >= lo && n <= hi)
        [ (0x1100, 0x115F), (0x2E80, 0xA4CF), (0xAC00, 0xD7A3), (0xF900, 0xFAFF)
        , (0xFE30, 0xFE4F), (0xFF00, 0xFF60), (0xFFE0, 0xFFE6), (0x1F300, 0x1FAFF)
        , (0x20000, 0x3FFFD)
        ]

-- | All groups, each one starting from a red line.
layoutGroups :: Int -> Int -> [LetterGroup] -> [Text]
layoutGroups width indent = concatMap (layoutGroup width indent . map render . groupWords)

-- | Counts shown by the @--stats@ option.
data Statistics = Statistics
  { paragraphCount :: Int
  , sentenceCount :: Int
  , wordCount :: Int
  , distinctWordCount :: Int
  , numberCount :: Int
  , punctuationCount :: Int
  , symbolCount :: Int
  , letterCount :: Int
  }
  deriving (Show, Eq)

statistics :: Document -> Statistics
statistics document@(Document paragraphs) =
  Statistics
    { paragraphCount = length paragraphs
    , sentenceCount = length sentences
    , wordCount = length (wordsOf document)
    , distinctWordCount = length distinct
    , numberCount = length [() | NumberElement _ <- elements]
    , punctuationCount = length [() | PunctuationElement _ <- elements]
    , symbolCount = length [() | SymbolElement _ <- elements]
    , -- The number of groups, without sorting the words.
      letterCount = Set.size (Set.fromList (map firstLetter distinct))
    }
  where
    sentences = [s | Paragraph ss <- paragraphs, s <- ss]
    elements = [e | Sentence es <- sentences, e <- es]
    distinct = distinctWords (wordsOf document)
