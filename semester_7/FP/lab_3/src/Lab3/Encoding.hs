-- | Decoding of input files: UTF-8 (checked) and Windows-1251, the
-- encoding of many older Ukrainian texts.
module Lab3.Encoding
  ( Encoding (..)
  , decode
  ) where

import Data.Array (Array, listArray, (!))
import qualified Data.ByteString as B
import Data.Text (Text)
import qualified Data.Text as T
import Data.Text.Encoding (decodeUtf8')
import Data.Word (Word8)

data Encoding = Utf8 | Cp1251
  deriving (Show, Eq)

-- | Decode the bytes of a file. Invalid UTF-8 is reported instead of being
-- replaced silently, so a file in another encoding cannot turn into an
-- empty result.
decode :: Encoding -> B.ByteString -> Either String Text
decode Utf8 bytes = case decodeUtf8' bytes of
  Right text -> Right text
  Left _ -> Left "the file is not valid UTF-8; if it is in Windows-1251, use --encoding cp1251"
decode Cp1251 bytes = Right (T.pack (map cp1251 (B.unpack bytes)))

-- | A byte of Windows-1251: the lower half is ASCII, the upper half is
-- 'upperHalf'.
cp1251 :: Word8 -> Char
cp1251 b
  | b < 0x80 = toEnum (fromIntegral b)
  | otherwise = upperHalf ! b

-- | Characters for the bytes 0x80..0xFF (0x98 is unused and becomes U+FFFD).
upperHalf :: Array Word8 Char
upperHalf =
  listArray
    (0x80, 0xFF)
    [
      '\x0402', '\x0403', '\x201A', '\x0453', '\x201E', '\x2026', '\x2020', '\x2021',
      '\x20AC', '\x2030', '\x0409', '\x2039', '\x040A', '\x040C', '\x040B', '\x040F',
      '\x0452', '\x2018', '\x2019', '\x201C', '\x201D', '\x2022', '\x2013', '\x2014',
      '\xFFFD', '\x2122', '\x0459', '\x203A', '\x045A', '\x045C', '\x045B', '\x045F',
      '\x00A0', '\x040E', '\x045E', '\x0408', '\x00A4', '\x0490', '\x00A6', '\x00A7',
      '\x0401', '\x00A9', '\x0404', '\x00AB', '\x00AC', '\x00AD', '\x00AE', '\x0407',
      '\x00B0', '\x00B1', '\x0406', '\x0456', '\x0491', '\x00B5', '\x00B6', '\x00B7',
      '\x0451', '\x2116', '\x0454', '\x00BB', '\x0458', '\x0405', '\x0455', '\x0457',
      '\x0410', '\x0411', '\x0412', '\x0413', '\x0414', '\x0415', '\x0416', '\x0417',
      '\x0418', '\x0419', '\x041A', '\x041B', '\x041C', '\x041D', '\x041E', '\x041F',
      '\x0420', '\x0421', '\x0422', '\x0423', '\x0424', '\x0425', '\x0426', '\x0427',
      '\x0428', '\x0429', '\x042A', '\x042B', '\x042C', '\x042D', '\x042E', '\x042F',
      '\x0430', '\x0431', '\x0432', '\x0433', '\x0434', '\x0435', '\x0436', '\x0437',
      '\x0438', '\x0439', '\x043A', '\x043B', '\x043C', '\x043D', '\x043E', '\x043F',
      '\x0440', '\x0441', '\x0442', '\x0443', '\x0444', '\x0445', '\x0446', '\x0447',
      '\x0448', '\x0449', '\x044A', '\x044B', '\x044C', '\x044D', '\x044E', '\x044F'
    ]
