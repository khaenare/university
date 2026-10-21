-- | Types of the text model: symbol, word, number, punctuation mark,
-- sentence, paragraph and the whole text.
module Lab3.Types
  ( Symbol (..)
  , Word (..)
  , Number (..)
  , PunctuationKind (..)
  , Punctuation (..)
  , Element (..)
  , Sentence (..)
  , Paragraph (..)
  , Document (..)
  , Render (..)
  , HasWords (..)
  , symbolChar
  , wordString
  ) where

import Prelude hiding (Word)

import Data.Text (Text)
import qualified Data.Text as T

-- | One character of the text other than a space (Символ).
newtype Symbol = Symbol Char
  deriving (Show, Eq, Ord)

symbolChar :: Symbol -> Char
symbolChar (Symbol c) = c

-- | A word (Слово): letters, digits and underscores, possibly joined by
-- apostrophes or hyphens (пам'ять, будь-який, my_value). A word contains
-- at least one letter; runs of digits alone are numbers.
newtype Word = Word [Symbol]
  deriving (Show, Eq)

wordString :: Word -> String
wordString (Word symbols) = map symbolChar symbols

-- | A number (Число): digits with an optional decimal point or comma (3,14).
newtype Number = Number [Symbol]
  deriving (Show, Eq)

-- | Role of a punctuation mark.
data PunctuationKind
  = -- | . ! ? …
    SentenceEnd
  | -- | , ; :
    Separator
  | -- | — – -
    Dash
  | -- | ( [ « „
    Opening
  | -- | ) ] »
    Closing
  | -- | " ' “ ” ‘ ’ (the same mark may open or close a quotation)
    Quote
  deriving (Show, Eq)

-- | A punctuation mark (Розділовий знак).
data Punctuation = Punctuation
  { punctuationKind :: PunctuationKind
  , punctuationSymbol :: Symbol
  }
  deriving (Show, Eq)

-- | A part of a sentence.
data Element
  = WordElement Word
  | NumberElement Number
  | PunctuationElement Punctuation
  | -- | Any other character, e.g. the operators of a code fragment (+, =, >).
    SymbolElement Symbol
  | -- | One space in place of any run of spaces, tabs and line breaks.
    Space
  deriving (Show, Eq)

-- | A sentence (Речення, «пропозиція» in the assignment).
newtype Sentence = Sentence [Element]
  deriving (Show, Eq)

-- | A paragraph: text between blank lines.
newtype Paragraph = Paragraph [Sentence]
  deriving (Show, Eq)

-- | The whole text (Текст).
newtype Document = Document [Paragraph]
  deriving (Show, Eq)

-- | Turning a part of the text back into characters. Every whitespace run
-- was already replaced by a single 'Space', so the result never contains
-- tabs or repeated spaces.
class Render a where
  render :: a -> Text

instance Render Symbol where
  render = T.singleton . symbolChar

instance Render Word where
  render = T.pack . wordString

instance Render Number where
  render (Number symbols) = T.pack (map symbolChar symbols)

instance Render Punctuation where
  render = render . punctuationSymbol

instance Render Element where
  render (WordElement w) = render w
  render (NumberElement n) = render n
  render (PunctuationElement p) = render p
  render (SymbolElement s) = render s
  render Space = " "

instance Render Sentence where
  render (Sentence elements) = T.concat (map render elements)

-- | Sentences of a paragraph are separated by one space.
instance Render Paragraph where
  render (Paragraph sentences) = T.intercalate " " (map render sentences)

-- | Paragraphs are separated by an empty line.
instance Render Document where
  render (Document paragraphs) = T.intercalate "\n\n" (map render paragraphs)

-- | Parts of the text that consist of words.
class HasWords a where
  wordsOf :: a -> [Word]

instance HasWords Sentence where
  wordsOf (Sentence elements) = [w | WordElement w <- elements]

instance HasWords Paragraph where
  wordsOf (Paragraph sentences) = concatMap wordsOf sentences

instance HasWords Document where
  wordsOf (Document paragraphs) = concatMap wordsOf paragraphs
