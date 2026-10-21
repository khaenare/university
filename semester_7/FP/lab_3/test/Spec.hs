-- | Tests of the text model, the alphabetical order and variant 6.
module Main (main) where

import Prelude hiding (Word)

import Control.Monad (unless)
import qualified Data.ByteString as B
import Data.Char (isSpace)
import Data.List (nub, sortBy)
import qualified Data.Text as T
import qualified Data.Text.IO as TIO
import System.Exit (exitFailure)
import Test.QuickCheck

import Lab3.Alphabet (compareWords, firstLetter, rank)
import Lab3.Encoding (Encoding (..), decode)
import Lab3.Parse (paragraphTexts, parseDocument, tokenize)
import Lab3.Task
import Lab3.Types

-- Generators -----------------------------------------------------------------

-- | Text of a "textbook": Latin and Cyrillic letters, digits, punctuation,
-- code symbols, apostrophes, all kinds of whitespace, and the characters
-- that real files contain: carriage returns, byte order marks, soft
-- hyphens, zero-width spaces, combining marks, the Unicode hyphen and Latin
-- letters with diacritics.
newtype Book = Book String
  deriving (Show)

instance Arbitrary Book where
  arbitrary = Book <$> listOf piece
    where
      piece =
        frequency
          [ (30, elements "абвгґдеєжзиіїйклмнопрстуфхцчшщьюяАБВҐЄІЇЮЯ")
          , (15, elements "abcdefghijklmnopqrstuvwxyzABCXYZ")
          , (6, elements "0123456789")
          , (10, elements ".,;:!?…—–-()[]«»\"'’ʼ")
          , (4, elements "+=*`#_/<>")
          , (20, elements " \t\n\xA0")
          , -- extra line breaks, so that blank lines (paragraphs) occur
            (4, pure '\n')
          , (3, elements "\r\xFEFF\xAD\x200B\x301\x306\x308\x2010éüÉł")
          ]
  shrink (Book s) = map Book (shrink s)

parse :: Book -> Document
parse (Book s) = parseDocument (T.pack s)

-- | A word built by the tokenizer from a random piece of text.
randomWords :: Gen [Word]
randomWords = wordsOf . parse <$> arbitrary

-- Properties of the text model ---------------------------------------------------

-- | Nothing but whitespace is lost or added by tokenizing: the elements of
-- the parsed text contain exactly the non-space characters of the prepared
-- paragraphs (after composition, removal of format characters and joining
-- of hyphenated lines, which 'paragraphTexts' does).
prop_keepsCharacters :: Book -> Property
prop_keepsCharacters book@(Book s) =
  filter (not . isSpace) (T.unpack (render (parse book)))
    === filter (not . isSpace) (concatMap T.unpack (paragraphTexts (T.pack s)))

-- | The rendered text has no tabs, no repeated spaces and no spaces at the
-- ends of lines.
prop_normalizesWhitespace :: Book -> Property
prop_normalizesWhitespace book =
  counterexample (show out) $
    not ("\t" `T.isInfixOf` out)
      && not ("  " `T.isInfixOf` out)
      && all (\l -> T.strip l == l) (T.lines out)
  where
    out = render (parse book)

-- | Parsing the rendered text gives the same structure again.
prop_idempotent :: Book -> Property
prop_idempotent book = parseDocument (render d) === d
  where
    d = parse book

-- Properties of variant 6 ------------------------------------------------------

-- | Groups are in alphabetical order, every word of a group starts with its
-- letter, and the words are sorted.
prop_groupsSorted :: Book -> Bool -> Property
prop_groupsSorted book keep =
  counterexample (show groups) $
    and [all ((== groupLetter g) . firstLetter) (groupWords g) | g <- groups]
      && strictlyIncreasing (map (rank . groupLetter) groups)
      && sortedBy compareWords (concatMap groupWords groups)
  where
    groups = groupByFirstLetter keep (parse book)
    strictlyIncreasing xs = and (zipWith (<) xs (drop 1 xs))
    sortedBy cmp xs = and (zipWith (\a b -> cmp a b /= GT) xs (drop 1 xs))

-- | With repeats every occurrence is listed; without them every word once.
prop_groupsCount :: Book -> Property
prop_groupsCount book =
  length (concatMap groupWords (groupByFirstLetter True d)) === length ws
    .&&. length (concatMap groupWords (groupByFirstLetter False d)) === length (distinctWords ws)
    .&&. length (nub (map identity (distinctWords ws))) === length (nub (map identity ws))
  where
    d = parse book
    ws = wordsOf d
    identity = T.toLower . T.replace "\x2010" "-" . T.replace "’" "'" . T.replace "ʼ" "'" . render

-- | The red line: the first line of a group is indented, the others are
-- not; lines fit the width unless they hold a single long word; no word is
-- lost or reordered.
prop_layout :: Property
prop_layout =
  forAll randomWords $ \ws -> forAll (chooseInt (20, 60)) $ \width -> forAll (chooseInt (0, 8)) $ \indent ->
    let texts = map render ws
        lines' = layoutGroup width indent texts
     in not (null texts) ==>
          counterexample (unlines (map T.unpack lines'))
            ( case lines' of
                first : rest ->
                  T.replicate indent " " `T.isPrefixOf` first
                    && not (" " `T.isPrefixOf` T.drop indent first)
                    && not (any (" " `T.isPrefixOf`) rest)
                [] -> False
            )
            .&&. all (\l -> displayWidth l <= width || length (T.words l) == 1) lines'
            .&&. concatMap T.words lines' === texts

-- Examples ---------------------------------------------------------------------------

example :: (Eq a, Show a) => String -> a -> a -> Property
example name actual expected = counterexample name (actual === expected)

wordsIn :: T.Text -> [String]
wordsIn = map wordString . wordsOf . parseDocument

sentencesIn :: T.Text -> [T.Text]
sentencesIn t = [render s | Paragraph ss <- [p | let Document ps = parseDocument t, p <- ps], s <- ss]

prop_examples :: Property
prop_examples =
  conjoin
    [ example "Ukrainian alphabet"
        (map wordString (sortBy compareWords (map w ["яблуко", "їжак", "іній", "ирій", "єнот", "етап", "ґанок", "гора", "Zebra", "apple", "2D"])))
        ["apple", "2D", "Zebra", "гора", "ґанок", "етап", "єнот", "ирій", "іній", "їжак", "яблуко"]
    , example "apostrophe is ignored when sorting"
        (map wordString (sortBy compareWords (map w ["пам'ять", "памфлет"])))
        ["памфлет", "пам'ять"]
    , example "words with apostrophes and hyphens"
        (wordsIn "пам'ять, об’єкт, імʼя і будь-який 64-бітний x1 my_value")
        ["пам'ять", "об’єкт", "імʼя", "і", "будь-який", "64-бітний", "x1", "my_value"]
    , example "C++ is a word and two symbols" (tokenize "C++")
        [WordElement (w "C"), SymbolElement (Symbol '+'), SymbolElement (Symbol '+')]
    , example "decimal numbers" (tokenize "3,14 і 1, 2")
        [ NumberElement (number "3,14"), Space, WordElement (w "і"), Space
        , NumberElement (number "1"), PunctuationElement (Punctuation Separator (Symbol ',')), Space
        , NumberElement (number "2")
        ]
    , example "quotes around a word" (wordsIn "'цитата' і кінець-") ["цитата", "і", "кінець"]
    , example "abbreviations and decimals do not end a sentence"
        (sentencesIn "Числа, напр. 3,14 і т. д. Отже, все. Далі System.out.println викликає метод.")
        ["Числа, напр. 3,14 і т. д.", "Отже, все.", "Далі System.out.println викликає метод."]
    , example "marks after the end belong to the sentence"
        (sentencesIn "Він сказав: \"Привіт!\". Що?! Так… «Нове» речення.")
        ["Він сказав: \"Привіт!\".", "Що?!", "Так…", "«Нове» речення."]
    , example "tabs, spaces and line breaks"
        (render (parseDocument "\tПерший  рядок\nтого ж абзацу.\n\n\n   Другий\t\tабзац.  "))
        "Перший рядок того ж абзацу.\n\nДругий абзац."
    , example "the least capitalized spelling is kept"
        (map wordString (distinctWords (map w ["Програма", "Haskell", "програма", "HASKELL", "Імʼя", "ім'я"])))
        ["програма", "Haskell", "ім'я"]
    , example "hyphen variants are one word"
        (map wordString (distinctWords (map w ["будь-який", "будь\x2010який"])))
        ["будь-який"]
    , example "decomposed letters are composed (NFC)"
        (wordsIn "\x0406\x0308жак і \x0438\x0306орж")
        ["Їжак", "і", "йорж"]
    , example "a stress mark stays inside the word" (wordsIn "за\x0301мок") ["за\x0301мок"]
    , example "soft hyphens and zero-width spaces are removed"
        (wordsIn "Програ\xADмування — мис\x200Bтецтво")
        ["Програмування", "мистецтво"]
    , example "words hyphenated at line ends are joined"
        (wordsIn "Основи програ-\nмування на X-\nWindow")
        ["Основи", "програмування", "на", "X", "Window"]
    , example "carriage returns and the byte order mark"
        (render (parseDocument "\xFEFFПерший\r\nрядок.\r\n\r\nДругий."))
        "Перший рядок.\n\nДругий."
    , example "Latin letters with diacritics sort by their base letter"
        (map wordString (sortBy compareWords (map w ["Über", "edit", "École", "eagle", "café", "cafe"])))
        ["cafe", "café", "eagle", "École", "edit", "Über"]
    , example "a word with leading digits belongs to its first letter"
        (map firstLetter [w "64-бітний", w "1-й", w "x1"])
        "бйx"
    , example "abbreviations do not end a sentence"
        (sentencesIn "Мови, напр. Java чи Python, e.g. Haskell. Див. рис. 3 і табл. 2. Кінець.")
        ["Мови, напр. Java чи Python, e.g. Haskell.", "Див. рис. 3 і табл. 2.", "Кінець."]
    , example "Windows-1251" (decode Cp1251 cp1251Bytes) (Right "Ґанок їжак Є")
    , example "Windows-1251 is not taken for UTF-8" (either (const True) (const False) (decode Utf8 cp1251Bytes)) True
    ]
  where
    w = Word . map Symbol
    number = Number . map Symbol
    -- "Ґанок їжак Є" in Windows-1251.
    cp1251Bytes = B.pack [0xA5, 0xE0, 0xED, 0xEE, 0xEA, 0x20, 0xBF, 0xE6, 0xE0, 0xEA, 0x20, 0xAA]

-- | The sample text: Latin comes before Cyrillic, ґ, є, ї have their own
-- groups, and "64-бітний" is in the group of б.
prop_sampleText :: Property
prop_sampleText = ioProperty $ do
  text <- TIO.readFile "data/textbook.txt"
  let groups = groupByFirstLetter False (parseDocument text)
      letters = map groupLetter groups
  pure $
    counterexample (show letters) $
      take 1 letters == "b"
        && [map wordString (groupWords g) | g <- groups, groupLetter g == '\x431'] == [["64-бітний", "б", "багато", "Бо", "будь-яку"]]
        && all (`elem` letters) ("bcgjx" ++ "\x430\x431\x432\x491\x434\x435\x454\x456\x457\x439\x44E\x44F")
        && indexOf 'x' letters < indexOf 'а' letters
        && indexOf 'в' letters < indexOf 'ґ' letters
        && indexOf 'е' letters < indexOf 'є' letters
        && indexOf 'і' letters < indexOf 'ї' letters
  where
    indexOf c = length . takeWhile (/= c)

main :: IO ()
main = do
  results <-
    sequence
      [ check "nothing but whitespace is lost" 1000 prop_keepsCharacters
      , check "whitespace is normalized" 1000 prop_normalizesWhitespace
      , check "parsing the rendered text gives the same text" 1000 prop_idempotent
      , check "groups and words are sorted" 1000 prop_groupsSorted
      , check "word counts with and without repeats" 1000 prop_groupsCount
      , check "red line layout" 1000 prop_layout
      , check "examples" 1 prop_examples
      , check "sample textbook" 1 prop_sampleText
      ]
  unless (and results) exitFailure
  where
    check :: Testable prop => String -> Int -> prop -> IO Bool
    check name n prop = do
      putStrLn ("--- " ++ name)
      isSuccess <$> quickCheckWithResult stdArgs {maxSuccess = n} prop
