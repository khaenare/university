-- | Aligned tables that are also valid Markdown, so benchmark output can be
-- pasted into the report as is.
module Lab2.Table
  ( renderTable
  ) where

import Data.List (intercalate, transpose)

renderTable :: [String] -> [[String]] -> [String]
renderTable names rows = line names : separator : map line rows
  where
    widths = map (maximum . map length) (transpose (names : rows))
    pad w s = s ++ replicate (w - length s) ' '
    line cells = "| " ++ intercalate " | " (zipWith pad widths cells) ++ " |"
    separator = "|" ++ intercalate "|" [replicate (w + 2) '-' | w <- widths] ++ "|"
