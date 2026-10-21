-- | Interactive entry and editing of records.
module Lab1.Form
  ( Form (..)
  , pickRecord
  , askRef
  , saveForm
  ) where

import Control.Exception (throwIO, try)
import Control.Monad (forM_, unless, when)
import Data.List (find)
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.IO as TIO
import qualified Database.MySQL.Base as Base
import Database.MySQL.Simple (Connection)

import Lab1.Console (AppError (..), ask, askField, cancelKey, confirm, showT)
import Lab1.Entity (Entity (..), countAll, findAll, findById, searchEntity)

-- | A record that the user can enter or edit from the console.
class Form a where
  -- | Ask for every field. With @Just old@ the stored values are the defaults.
  form :: Connection -> Maybe a -> IO a

  -- | Business rules checked before saving; returns error messages.
  validate :: a -> [Text]
  validate _ = []

  -- | Rules that need to look at other records, e.g. schedule conflicts.
  validateWith :: Connection -> a -> IO [Text]
  validateWith _ _ = pure []

-- | Fill the form and save the record with @save@.
--
-- When a rule or the database rejects the record, the user can fix the
-- values; what was typed is kept as the new defaults.
saveForm :: Form a => Connection -> Maybe a -> (a -> IO r) -> IO r
saveForm conn current save = do
  TIO.putStrLn ("Type " <> cancelKey <> " at any prompt to cancel.")
  loop current
  where
    loop defaults = do
      record <- form conn defaults
      errors <- case validate record of
        [] -> validateWith conn record
        errors -> pure errors
      if not (null errors)
        then retry record errors
        else do
          result <- try (save record)
          case result of
            Right saved -> pure saved
            Left (e :: Base.MySQLError) -> retry record ["Database error: " <> T.pack (Base.errMessage e)]
    retry record errors = do
      forM_ errors $ \e -> TIO.putStrLn ("  ! " <> e)
      again <- confirm "Fix the values?"
      unless again $ throwIO (UserError "The record was not saved.")
      loop (Just record)

-- | Tables with more records than this are filtered before listing.
listLimit :: Int
listLimit = 15

-- | Let the user choose a related record by its ID.
--
-- Small tables are listed in full; for larger ones the user first types a
-- filter, so the prompt does not print the whole table.
pickRecord :: forall e. Entity e => Connection -> Text -> Maybe Int -> IO e
pickRecord conn label current = do
  total <- countAll @e conn
  when (total == 0) $
    throwIO (UserError ("There is no " <> entityName @e <> " yet, add one first."))
  shown <-
    if total <= listLimit
      then findAll @e conn
      else do
        term <- ask ("  Filter " <> entityName @e <> " records (part of the text, Enter for all): ")
        if T.null term then findAll @e conn else searchEntity @e conn term
  if null shown
    then TIO.putStrLn "  (no matching records)"
    else do
      TIO.putStrLn ("  Available " <> entityName @e <> " records:")
      forM_ shown $ \r -> TIO.putStrLn ("    " <> showT (entityId r) <> ". " <> summary r)
  let loop = do
        key <- askField (label <> " ID") current
        case find ((== key) . entityId) shown of
          Just record -> pure record
          Nothing -> findById @e conn key >>= maybe (TIO.putStrLn "  No record with this ID." >> loop) pure
  loop

-- | Like 'pickRecord', but return only the ID (for foreign key fields).
askRef :: forall e. Entity e => Connection -> Text -> Maybe Int -> IO Int
askRef conn label current = entityId <$> pickRecord @e conn label current
