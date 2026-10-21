-- | Reading a text into the model of "Lab3.Types".
module Lab3.Parse
  ( parseDocument
  , prepare
  , paragraphTexts
  , tokenize
  , splitSentences
  , classifyPunctuation
  , isApostrophe
  ) where

import Prelude hiding (Word)

import Data.Char (GeneralCategory (Format), generalCategory, isAlphaNum, isDigit, isLetter, isLower, isMark, isSpace, toLower)
import Data.List (dropWhileEnd)
import Data.Text (Text)
import qualified Data.Text as T
import Data.Text.Normalize (NormalizationMode (NFC), normalize)

import Lab3.Types

-- | Parse a whole text. Paragraphs are separated by blank lines; inside a
-- paragraph line breaks, tabs and runs of spaces all become one space.
parseDocument :: Text -> Document
parseDocument =
  Document . filter (\(Paragraph s) -> not (null s)) . map parseParagraph . paragraphTexts

-- | Clean up the characters before parsing:
--
-- * compose letters (NFC), so that ї written as і + U+0308 is one letter;
-- * drop invisible format characters: soft hyphens, zero-width spaces, the
--   byte order mark;
-- * drop carriage returns of Windows line ends.
prepare :: Text -> Text
prepare = T.filter (\c -> c /= '\r' && generalCategory c /= Format) . normalize NFC

-- | The text of every paragraph, with its lines joined.
paragraphTexts :: Text -> [Text]
paragraphTexts = map (joinLines . map T.strip) . splitOnBlankLines . T.lines . prepare

-- | Join the lines of a paragraph with spaces. A word hyphenated at the end
-- of a line ("програ-" + "мування") is joined back without the hyphen when
-- the next line starts with a lower-case letter.
joinLines :: [Text] -> Text
joinLines lines' = case filter (not . T.null) lines' of
  [] -> T.empty
  first : rest -> foldl join first rest
  where
    join done next
      | hyphenated done, Just (c, _) <- T.uncons next, isLower c = T.init done <> next
      | otherwise = done <> " " <> next
    hyphenated line = case T.unpack (T.takeEnd 2 line) of
      [l, h] -> isLetter l && isHyphen h
      _ -> False

splitOnBlankLines :: [Text] -> [[Text]]
splitOnBlankLines lines' = case dropWhile isBlank lines' of
  [] -> []
  rest -> let (paragraph, more) = break isBlank rest in paragraph : splitOnBlankLines more
  where
    isBlank = T.all isSpace

parseParagraph :: Text -> Paragraph
parseParagraph = Paragraph . splitSentences . tokenize . T.unpack

-- | Split characters into elements; every run of whitespace becomes one
-- 'Space'.
tokenize :: String -> [Element]
tokenize [] = []
tokenize s@(c : rest)
  | isSpace c = Space : tokenize (dropWhile isSpace rest)
  | isWordChar c =
      let (run, afterRun) = spanWord s
       in if any isLetter run
            then WordElement (Word (map Symbol run)) : tokenize afterRun
            else
              if isDigit c
                then
                  let (digits, afterNumber) = spanNumber s
                   in NumberElement (Number (map Symbol digits)) : tokenize afterNumber
                else -- underscores without letters: ordinary symbols
                  SymbolElement (Symbol c) : tokenize rest
  | Just kind <- classifyPunctuation c = PunctuationElement (Punctuation kind (Symbol c)) : tokenize rest
  | otherwise = SymbolElement (Symbol c) : tokenize rest

isWordChar :: Char -> Bool
isWordChar c = (isAlphaNum c || c == '_') && not (isApostrophe c)

-- | Apostrophes used in Ukrainian words: ', ’ and the modifier letter ʼ.
isApostrophe :: Char -> Bool
isApostrophe c = c `elem` ("'\x2019\x02BC" :: String)

-- | The hyphen-minus and the Unicode hyphen U+2010.
isHyphen :: Char -> Bool
isHyphen c = c == '-' || c == '\x2010'

-- | Characters that may join two parts of one word.
isJoiner :: Char -> Bool
isJoiner c = isApostrophe c || isHyphen c

-- | The longest word at the start: word characters, with single joiners
-- between them (a joiner at the end does not belong to the word).
-- Combining marks left after composition (e.g. the stress mark U+0301)
-- belong to the letter before them.
spanWord :: String -> (String, String)
spanWord = go []
  where
    go acc (c : rest)
      | isWordChar c || (not (null acc) && isMark c) = go (c : acc) rest
    go acc (j : c : rest)
      | not (null acc) && isJoiner j && isWordChar c = go (c : j : acc) rest
    go acc rest = (reverse acc, rest)

-- | The longest number at the start: digits, with a decimal point or comma
-- between digits (3.14, 3,14).
spanNumber :: String -> (String, String)
spanNumber = go []
  where
    go acc (c : rest)
      | isDigit c = go (c : acc) rest
    go acc (sep : c : rest)
      | not (null acc) && all isDigit acc && sep `elem` (".," :: String) && isDigit c =
          go (c : sep : acc) rest
    go acc rest = (reverse acc, rest)

-- | Punctuation marks of Ukrainian text. Other characters (+, =, *, /, #,
-- ...) are symbols, not punctuation.
classifyPunctuation :: Char -> Maybe PunctuationKind
classifyPunctuation c
  | c `elem` (".!?\x2026" :: String) = Just SentenceEnd
  | c `elem` (",;:" :: String) = Just Separator
  | c `elem` ("-\x2013\x2014" :: String) = Just Dash
  | c `elem` ("([\x00AB\x201E\x2039" :: String) = Just Opening
  | c `elem` (")]\x00BB\x203A" :: String) = Just Closing
  | c `elem` ("\"'\x201C\x201D\x2018\x2019" :: String) = Just Quote
  | otherwise = Nothing

-- | Split the elements of a paragraph into sentences.
--
-- A sentence ends with . ! ? or … (together with marks right after it,
-- like ?! or ." or .») when a space and the start of a new sentence
-- follow, or when the paragraph ends. A new sentence starts with a capital
-- letter, an opening bracket or quote, or a dash; so "т. д. та",
-- "напр. 3,14" or "System.out.println" do not end a sentence. The period
-- of an abbreviation such as "напр." or "e.g." never ends a sentence.
splitSentences :: [Element] -> [Sentence]
splitSentences = filter (\(Sentence e) -> not (null e)) . map (Sentence . trim) . go []
  where
    go acc [] = [reverse acc]
    go acc (e : rest)
      | isKind SentenceEnd e && not (isPeriod e && afterAbbreviation acc) =
          let (ends, afterEnds) = span attachesToEnd rest
              acc' = reverse ends ++ e : acc
           in case afterEnds of
                [] -> [reverse acc']
                Space : next | startsSentence next -> reverse acc' : go [] next
                _ -> go acc' afterEnds
      | otherwise = go (e : acc) rest
    attachesToEnd e = any (`isKind` e) [SentenceEnd, Closing, Quote]
    trim = dropWhileEnd (== Space) . dropWhile (== Space)

startsSentence :: [Element] -> Bool
startsSentence next = case next of
  WordElement (Word (Symbol c : _)) : _ -> not (isLower c) && not (isDigit c)
  PunctuationElement p : _ -> punctuationKind p `elem` [Opening, Quote, Dash]
  _ -> False

isKind :: PunctuationKind -> Element -> Bool
isKind kind (PunctuationElement p) = punctuationKind p == kind
isKind _ _ = False

isPeriod :: Element -> Bool
isPeriod (PunctuationElement p) = symbolChar (punctuationSymbol p) == '.'
isPeriod _ = False

-- | Abbreviations that are written with a period but are followed by more
-- of the same sentence (often a name or a number): "напр. Java",
-- "див. Розділ 2". Abbreviations that may also end a sentence ("т. д.",
-- "та ін.") are not listed.
abbreviations :: [String]
abbreviations = ["напр", "див", "рис", "табл", "мал", "розд", "підрозд", "стор", "порівн", "cf", "vs", "fig"]

-- | Whether the elements before a period (nearest first) end with an
-- abbreviation; "e.g." and "i.e." are two one-letter words with periods.
afterAbbreviation :: [Element] -> Bool
afterAbbreviation before = case before of
  WordElement w : p : WordElement v : _
    | isPeriod p, (lower v, lower w) `elem` [("e", "g"), ("i", "e")] -> True
  WordElement w : _ -> lower w `elem` abbreviations
  _ -> False
  where
    lower = map toLower . wordString
