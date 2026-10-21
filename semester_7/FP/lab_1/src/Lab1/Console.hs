-- | Console input/output helpers shared by all menus and forms.
module Lab1.Console
  ( Input (..)
  , AppError (..)
  , cancelKey
  , readLine
  , ask
  , askField
  , askOptional
  , confirm
  , showT
  , orDash
  , showMaybe
  , shorten
  , addMinutes
  , today
  ) where

import Control.Exception (Exception, throwIO)
import Control.Monad (join)
import Data.Int (Int32)
import Data.Maybe (fromMaybe)
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.IO as TIO
import Data.Time
  ( Day
  , TimeOfDay
  , defaultTimeLocale
  , formatTime
  , getZonedTime
  , localDay
  , parseTimeM
  , secondsToDiffTime
  , timeOfDayToTime
  , timeToTimeOfDay
  , zonedTimeToLocalTime
  )
import System.IO (hFlush, stdout)
import Text.Read (readMaybe)

-- | Errors caused by the user's actions, shown as plain messages.
data AppError
  = UserError Text
  | -- | The user typed 'cancelKey' at a prompt.
    Cancelled
  deriving (Show)

instance Exception AppError

-- | Answer that cancels the current form or prompt.
cancelKey :: Text
cancelKey = "!"

-- | Values that can be typed by the user and shown back as a default.
class Input a where
  parseInput :: Text -> Maybe a
  showInput :: a -> Text

  -- | Short description of the expected format, shown in the prompt.
  inputHint :: Text
  inputHint = ""

instance Input Text where
  parseInput t
    | T.null t = Nothing
    | otherwise = Just t
  showInput = id

-- | Numbers are limited to the range of the MySQL INT columns, so a huge
-- number is rejected instead of silently wrapping around.
instance Input Int where
  parseInput t = do
    n <- readMaybe (T.unpack t) :: Maybe Integer
    if n >= toInteger (minBound :: Int32) && n <= toInteger (maxBound :: Int32)
      then Just (fromInteger n)
      else Nothing
  showInput = showT
  inputHint = "number"

instance Input Day where
  parseInput = parseTimeM True defaultTimeLocale "%Y-%m-%d" . T.unpack
  showInput = T.pack . formatTime defaultTimeLocale "%Y-%m-%d"
  inputHint = "YYYY-MM-DD"

instance Input TimeOfDay where
  parseInput t =
    case parse "%H:%M" of
      Just v -> Just v
      Nothing -> parse "%H:%M:%S"
    where
      parse fmt = parseTimeM True defaultTimeLocale fmt (T.unpack t)
  showInput = T.pack . formatTime defaultTimeLocale "%H:%M"
  inputHint = "HH:MM"

showT :: Show a => a -> Text
showT = T.pack . show

-- | Text of an optional value, or "-" when it is missing.
orDash :: Maybe Text -> Text
orDash = fromMaybe "-"

showMaybe :: Input a => Maybe a -> Text
showMaybe = maybe "-" showInput

-- | Collapse whitespace and cut the text to at most @n@ characters.
shorten :: Int -> Text -> Text
shorten n value
  | T.length flat > n = T.take (n - 1) flat <> "…"
  | otherwise = flat
  where
    flat = T.unwords (T.words value)

-- | Time of day @m@ minutes later, capped at 23:59:59 (no day overflow).
addMinutes :: Int -> TimeOfDay -> TimeOfDay
addMinutes m t = timeToTimeOfDay (secondsToDiffTime (min lastSecond seconds))
  where
    seconds = floor (timeOfDayToTime t) + 60 * toInteger m
    lastSecond = 24 * 3600 - 1

-- | Current local date.
today :: IO Day
today = localDay . zonedTimeToLocalTime <$> getZonedTime

-- | Print a prompt and read one trimmed line.
--
-- Bytes that are not valid UTF-8 (for example from a terminal in another
-- encoding) are decoded as U+FFFD; such a line is rejected and asked again,
-- so broken text never reaches the database.
readLine :: Text -> IO Text
readLine prompt = do
  TIO.putStr prompt
  hFlush stdout
  line <- T.strip <$> TIO.getLine
  if T.any (== '\xFFFD') line
    then do
      TIO.putStrLn "  The input contains characters that cannot be decoded; check that the terminal uses UTF-8."
      readLine prompt
    else pure line

-- | Like 'readLine', but 'cancelKey' aborts the current action.
ask :: Text -> IO Text
ask prompt = do
  answer <- readLine prompt
  if answer == cancelKey then throwIO Cancelled else pure answer

-- | Build a prompt like "Deadline (YYYY-MM-DD) [2026-10-30]: ".
promptFor :: Text -> Text -> Maybe Text -> Text
promptFor label hint current =
  label <> hintPart <> currentPart <> ": "
  where
    hintPart = if T.null hint then "" else " (" <> hint <> ")"
    currentPart = maybe "" (\c -> " [" <> c <> "]") current

-- | Ask for a required value. An empty answer keeps the current value.
askField :: forall a. Input a => Text -> Maybe a -> IO a
askField label current = loop
  where
    loop = do
      answer <- ask (promptFor label (inputHint @a) (showInput <$> current))
      case (answer, current) of
        ("", Just old) -> pure old
        ("", Nothing) -> retry "A value is required."
        _ -> maybe (retry "Invalid value, please try again.") pure (parseInput answer)
    retry msg = TIO.putStrLn ("  " <> msg) >> loop

-- | Ask for an optional value.
--
-- The outer 'Maybe' tells whether there is a stored record: an empty answer
-- keeps the stored value, and "-" clears it.
askOptional :: forall a. Input a => Text -> Maybe (Maybe a) -> IO (Maybe a)
askOptional label current = loop
  where
    stored = join current
    hint = T.intercalate ", " (filter (not . T.null) [inputHint @a, "optional", "'-' to clear"])
    loop = do
      answer <- ask (promptFor label hint (showInput <$> stored))
      case answer of
        "" -> pure stored
        "-" -> pure Nothing
        _ -> maybe (TIO.putStrLn "  Invalid value, please try again." >> loop) (pure . Just) (parseInput answer)

-- | Ask a yes/no question.
confirm :: Text -> IO Bool
confirm question = do
  answer <- T.toLower <$> ask (question <> " (y/n): ")
  case answer of
    "y" -> pure True
    "yes" -> pure True
    "n" -> pure False
    "no" -> pure False
    _ -> confirm question
