module Main (main) where

import Control.Exception (IOException, try)
import qualified Data.ByteString as B
import Data.Text (Text)
import qualified Data.Text as T
import Data.Text.Encoding (encodeUtf8)
import qualified Data.Text.IO as TIO
import Options.Applicative
import System.Exit (exitFailure)
import System.IO (hPutStrLn, hSetEncoding, stderr, stdout, utf8)
import Text.Read (readMaybe)

import Lab3.Encoding (Encoding (..), decode)
import Lab3.Parse (parseDocument)
import Lab3.Task
import Lab3.Types

-- | What to print.
data Mode
  = -- | Variant 6: the words by first letter.
    WordsByLetter
  | -- | The text with whitespace normalised.
    NormalizedText
  | -- | Every sentence on its own line.
    Sentences
  | Stats

data Options = Options
  { optInput :: FilePath
  , optEncoding :: Encoding
  , optOutput :: Maybe FilePath
  , optMode :: Mode
  , optWidth :: Int
  , optIndent :: Int
  , optAll :: Bool
  }

optionsParser :: Parser Options
optionsParser =
  Options
    <$> strArgument (metavar "FILE" <> value "data/textbook.txt" <> showDefault
          <> help "Text file, or - for standard input")
    <*> option encodingReader (long "encoding" <> short 'e' <> metavar "utf8|cp1251" <> value Utf8
          <> showDefaultWith (const "utf8") <> help "Encoding of the input file")
    <*> optional (strOption (long "output" <> short 'o' <> metavar "FILE" <> help "Write the result to a file"))
    <*> modeParser
    <*> option (bounded 20 1000) (long "width" <> short 'w' <> metavar "N" <> value 80 <> showDefault
          <> help "Maximum line length")
    -- At least one space: without it a new letter could not be told apart
    -- from a wrapped line.
    <*> option (bounded 1 40) (long "indent" <> short 'i' <> metavar "N" <> value 4 <> showDefault
          <> help "Indent of the red line (first line of every letter)")
    <*> switch (long "all" <> short 'a' <> help "List every occurrence of a word, not each word once")
  where
    modeParser =
      flag' NormalizedText (long "text" <> help "Print the text with tabs and repeated spaces replaced by one space")
        <|> flag' Sentences (long "sentences" <> help "Print every sentence on its own line")
        <|> flag' Stats (long "stats" <> help "Print counts of paragraphs, sentences, words and marks")
        <|> pure WordsByLetter

encodingReader :: ReadM Encoding
encodingReader = eitherReader $ \s -> case s of
  "utf8" -> Right Utf8
  "utf-8" -> Right Utf8
  "cp1251" -> Right Cp1251
  "windows-1251" -> Right Cp1251
  _ -> Left "the encoding must be utf8 or cp1251"

bounded :: Int -> Int -> ReadM Int
bounded lo hi = eitherReader $ \s -> case readMaybe s of
  Just n | n >= lo && n <= hi -> Right n
  _ -> Left ("expected a number from " ++ show lo ++ " to " ++ show hi)

main :: IO ()
main = do
  hSetEncoding stdout utf8
  opts <- execParser (info (optionsParser <**> helper)
    (fullDesc <> progDesc "Print the words of a text in alphabetical order, every new letter from a red line"))
  case optMode opts of
    WordsByLetter | optIndent opts >= optWidth opts -> failWith "the indent must be smaller than the width"
    _ -> pure ()
  input <- readInput (optEncoding opts) (optInput opts)
  let document = parseDocument input
      result = T.unlines (produce opts document)
  case optOutput opts of
    Nothing -> TIO.putStr result
    Just path -> writeOutput path result

produce :: Options -> Document -> [Text]
produce opts document@(Document paragraphs) = case optMode opts of
  WordsByLetter -> layoutGroups (optWidth opts) (optIndent opts) (groupByFirstLetter (optAll opts) document)
  NormalizedText -> [render document]
  Sentences -> [render s | Paragraph ss <- paragraphs, s <- ss]
  Stats ->
    let st = statistics document
     in [ "Paragraphs:          " <> showT (paragraphCount st)
        , "Sentences:           " <> showT (sentenceCount st)
        , "Words:               " <> showT (wordCount st)
        , "Distinct words:      " <> showT (distinctWordCount st)
        , "Numbers:             " <> showT (numberCount st)
        , "Punctuation marks:   " <> showT (punctuationCount st)
        , "Other symbols:       " <> showT (symbolCount st)
        , "First letters:       " <> showT (letterCount st)
        ]
  where
    showT = T.pack . show

-- | Read and decode a file; a decoding problem is an error, not an empty
-- result.
readInput :: Encoding -> FilePath -> IO Text
readInput encoding path = do
  bytes <- try (if path == "-" then B.getContents else B.readFile path)
  case bytes of
    Right b -> either (\problem -> failWith (path ++ ": " ++ problem)) pure (decode encoding b)
    Left (e :: IOException) -> failWith ("cannot read " ++ path ++ ": " ++ show e)

writeOutput :: FilePath -> Text -> IO ()
writeOutput path text = do
  written <- try (B.writeFile path (encodeUtf8 text))
  case written of
    Right () -> pure ()
    Left (e :: IOException) -> failWith ("cannot write " ++ path ++ ": " ++ show e)

failWith :: String -> IO a
failWith message = hPutStrLn stderr ("Error: " ++ message) >> exitFailure
