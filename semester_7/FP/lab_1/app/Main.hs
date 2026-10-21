module Main (main) where

import Control.Exception (catch, finally, throwIO)
import qualified Data.Text as T
import qualified Data.Text.IO as TIO
import qualified Database.MySQL.Base as Base
import Database.MySQL.Simple (close, connect)
import System.Exit (exitFailure)
import System.IO (BufferMode (..), hSetBuffering, hSetEncoding, mkTextEncoding, stdin, stdout, utf8)
import System.IO.Error (isEOFError)

import Lab1.Config (loadConnectInfo)
import Lab1.Menu (mainMenu)

main :: IO ()
main = do
  -- Ukrainian data must be readable regardless of the terminal locale.
  hSetEncoding stdout utf8
  -- Invalid input bytes become U+FFFD instead of an exception;
  -- Lab1.Console rejects such lines.
  hSetEncoding stdin =<< mkTextEncoding "UTF-8//TRANSLIT"
  hSetBuffering stdout NoBuffering

  settings <- loadConnectInfo
  info <- case settings of
    Right info -> pure info
    Left problem -> do
      putStrLn ("Invalid settings: " ++ problem)
      exitFailure
  conn <- connect info `catch` \e -> do
    TIO.putStrLn ("Cannot connect to MySQL: " <> T.pack (Base.errMessage e))
    TIO.putStrLn "Check that the server is running and the LAB1_DB_* variables are correct."
    exitFailure

  (mainMenu conn `catch` onEndOfInput) `finally` close conn
  TIO.putStrLn "Bye!"
  where
    -- Finish quietly when the input ends (Ctrl+D or a piped script).
    onEndOfInput e
      | isEOFError e = TIO.putStrLn ""
      | otherwise = throwIO e
