-- | Type classes that describe database entities and generic CRUD
-- operations implemented once for every instance.
module Lab1.Entity
  ( Entity (..)
  , Tabular (..)
  , Dependent (..)
  , findAll
  , findById
  , countAll
  , insertEntity
  , updateEntity
  , deleteEntity
  , searchEntity
  , dependentRecords
  , printTable
  , printRecord
  , printRows
  ) where

import Control.Monad (forM, forM_)
import Data.List (intercalate, transpose)
import Data.Maybe (catMaybes, listToMaybe)
import Data.String (fromString)
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.IO as TIO
import Database.MySQL.Simple
  ( Connection
  , Only (..)
  , Query
  , execute
  , insertID
  , query
  , query_
  )
import Database.MySQL.Simple.Param (Action, render)
import Database.MySQL.Simple.QueryResults (QueryResults)

import Lab1.Console (shorten)

-- | A record stored in its own table with an auto-increment @id@ column.
--
-- 'QueryResults' (from mysql-simple) converts a result row into the record;
-- the row must contain @id@ followed by 'columns' in the same order.
class QueryResults a => Entity a where
  -- | Name of the table.
  tableName :: String

  -- | Human-readable singular name, used in messages.
  entityName :: Text

  -- | Data columns (without @id@), in the order of 'toParams'.
  columns :: [String]

  -- | Columns used by the text search.
  searchColumns :: [String]
  searchColumns = columns @a

  -- | ORDER BY expression for listings.
  orderColumn :: String
  orderColumn = "id"

  entityId :: a -> Int

  -- | Values of 'columns' for INSERT and UPDATE statements.
  toParams :: a -> [Action]

  -- | One-line description, used when the user picks a related record.
  summary :: a -> Text

-- | A record that can be printed as a table row.
class Tabular a where
  headers :: [Text]
  cells :: a -> [Text]

quote :: String -> String
quote name = "`" ++ name ++ "`"

sql :: String -> Query
sql = fromString

selectSql :: forall a. Entity a => String
selectSql =
  "SELECT " ++ intercalate ", " (map quote ("id" : columns @a))
    ++ " FROM " ++ quote (tableName @a)

findAll :: forall a. Entity a => Connection -> IO [a]
findAll conn = query_ conn (sql (selectSql @a ++ " ORDER BY " ++ orderColumn @a))

findById :: forall a. Entity a => Connection -> Int -> IO (Maybe a)
findById conn key =
  listToMaybe <$> query conn (sql (selectSql @a ++ " WHERE id = ?")) (Only key)

countAll :: forall a. Entity a => Connection -> IO Int
countAll conn = do
  rows <- query_ conn (sql ("SELECT COUNT(*) FROM " ++ quote (tableName @a)))
  pure (sum [n | Only n <- rows])

-- | Insert a record (its id is ignored) and return the generated id.
insertEntity :: forall a. Entity a => Connection -> a -> IO Int
insertEntity conn record = do
  _ <- execute conn (sql statement) (toParams record)
  fromIntegral <$> insertID conn
  where
    cols = columns @a
    statement =
      "INSERT INTO " ++ quote (tableName @a)
        ++ " (" ++ intercalate ", " (map quote cols) ++ ")"
        ++ " VALUES (" ++ intercalate ", " (map (const "?") cols) ++ ")"

-- | Update the stored record with the same id. Returns False if it is missing.
--
-- The connection uses the FoundRows flag, so the result counts matched rows
-- even when the new values are the same as the stored ones.
updateEntity :: forall a. Entity a => Connection -> a -> IO Bool
updateEntity conn record = do
  affected <- execute conn (sql statement) (toParams record ++ [render (entityId record)])
  pure (affected > 0)
  where
    statement =
      "UPDATE " ++ quote (tableName @a)
        ++ " SET " ++ intercalate ", " [quote c ++ " = ?" | c <- columns @a]
        ++ " WHERE id = ?"

-- | Delete a record by id. Returns False if it is missing.
deleteEntity :: forall a. Entity a => Connection -> Int -> IO Bool
deleteEntity conn key = do
  affected <- execute conn (sql ("DELETE FROM " ++ quote (tableName @a) ++ " WHERE id = ?")) (Only key)
  pure (affected > 0)

-- | Case-insensitive substring search over 'searchColumns'.
searchEntity :: forall a. Entity a => Connection -> Text -> IO [a]
searchEntity conn term = query conn (sql statement) (map (const pattern) cols)
  where
    cols = searchColumns @a
    statement =
      selectSql @a
        ++ " WHERE " ++ intercalate " OR " [quote c ++ " LIKE ?" | c <- cols]
        ++ " ORDER BY " ++ orderColumn @a
    pattern = "%" <> T.concatMap escape term <> "%"
    -- Treat LIKE wildcards typed by the user literally.
    escape c
      | c `elem` ['%', '_', '\\'] = T.pack ['\\', c]
      | otherwise = T.singleton c

-- | Rows of another table that reference a record through a foreign key.
data Dependent = Dependent
  { dependentTable :: String
  , dependentCount :: Int
  , -- | True for ON DELETE CASCADE, False when the reference blocks deletion.
    dependentCascades :: Bool
  }

-- | Count the rows that reference the record, using the foreign keys
-- declared in the database schema.
dependentRecords :: forall a. Entity a => Connection -> Int -> IO [Dependent]
dependentRecords conn key = do
  refs <-
    query
      conn
      "SELECT k.TABLE_NAME, k.COLUMN_NAME, r.DELETE_RULE \
      \FROM information_schema.KEY_COLUMN_USAGE k \
      \JOIN information_schema.REFERENTIAL_CONSTRAINTS r \
      \  ON r.CONSTRAINT_SCHEMA = k.CONSTRAINT_SCHEMA AND r.CONSTRAINT_NAME = k.CONSTRAINT_NAME \
      \WHERE k.TABLE_SCHEMA = DATABASE() AND k.REFERENCED_TABLE_NAME = ? \
      \ORDER BY k.TABLE_NAME"
      (Only (tableName @a))
  found <- forM refs $ \(table, column, rule) -> do
    rows <-
      query conn (sql ("SELECT COUNT(*) FROM " ++ quote table ++ " WHERE " ++ quote column ++ " = ?")) (Only key)
    let count = sum [n | Only n <- rows]
    pure (if count > 0 then Just (Dependent table count (rule == ("CASCADE" :: String))) else Nothing)
  pure (catMaybes found)

-- | Print records as a table.
printTable :: forall a. Tabular a => [a] -> IO ()
printTable records = printRows (headers @a) (map cells records)

-- | Print one record vertically, without shortening long values.
printRecord :: forall a. Tabular a => a -> IO ()
printRecord record =
  forM_ (zip (headers @a) (cells record)) $ \(name, value) ->
    TIO.putStrLn (T.justifyLeft width ' ' name <> " : " <> value)
  where
    width = maximum (map T.length (headers @a))

-- | Print arbitrary rows as an aligned text table.
printRows :: [Text] -> [[Text]] -> IO ()
printRows names rows
  | null rows = TIO.putStrLn "(no records)"
  | otherwise = do
      mapM_ TIO.putStrLn (line names : separator : map line clipped)
      TIO.putStrLn (T.pack (show (length rows)) <> " record(s)")
  where
    clipped = map (map clip) rows
    widths = map (maximum . map T.length) (transpose (names : clipped))
    line values = T.stripEnd (T.intercalate " | " (zipWith pad widths values))
    pad width value = T.justifyLeft width ' ' value
    separator = T.intercalate "-+-" [T.replicate w "-" | w <- widths]

-- | Maximum width of a table cell.
clip :: Text -> Text
clip = shorten 40
