-- | Database connection settings, read from environment variables.
module Lab1.Config
  ( loadConnectInfo
  ) where

import Data.Maybe (fromMaybe)
import Data.Word (Word16)
import Database.MySQL.Base (ConnectInfo (..), Option (..), defaultConnectInfo)
import System.Environment (lookupEnv)
import Text.Read (readMaybe)

-- | Settings with defaults for a local MySQL server:
--
-- * @LAB1_DB_HOST@     (default @127.0.0.1@)
-- * @LAB1_DB_PORT@     (default @3306@)
-- * @LAB1_DB_USER@     (default @root@)
-- * @LAB1_DB_PASSWORD@ (default empty)
-- * @LAB1_DB_NAME@     (default @dept_individual_work@)
--
-- The default host is an IP address on purpose: for the host name
-- @localhost@ the MySQL client uses the Unix socket and ignores the port.
loadConnectInfo :: IO (Either String ConnectInfo)
loadConnectInfo = do
  host <- env "LAB1_DB_HOST" "127.0.0.1"
  portText <- env "LAB1_DB_PORT" "3306"
  user <- env "LAB1_DB_USER" "root"
  password <- env "LAB1_DB_PASSWORD" ""
  database <- env "LAB1_DB_NAME" "dept_individual_work"
  pure $ case parsePort portText of
    Nothing -> Left ("LAB1_DB_PORT must be a number from 1 to 65535, got " ++ show portText)
    Just port ->
      Right
        defaultConnectInfo
          { connectHost = host
          , connectPort = port
          , connectUser = user
          , connectPassword = password
          , connectDatabase = database
          , connectOptions =
              [ -- Store and read Ukrainian text correctly.
                CharsetName "utf8mb4"
              , -- UPDATE reports matched rows, not only changed ones.
                FoundRows
              ]
          }
  where
    env name def = fromMaybe def <$> lookupEnv name

parsePort :: String -> Maybe Word16
parsePort text = do
  n <- readMaybe text :: Maybe Integer
  if n >= 1 && n <= 65535 then Just (fromInteger n) else Nothing
