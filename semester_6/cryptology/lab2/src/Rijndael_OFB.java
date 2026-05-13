import java.nio.charset.StandardCharsets;

public class Rijndael_OFB {

    private final Rijndael cipher;

    /**
     * @param key 128-бітний ключ Rijndael (16 байт)
     */
    public Rijndael_OFB(byte[] key) {
        this.cipher = new Rijndael(key);
    }

    // генерація keystream і XOR із даними

    /**
     * шифрує або розшифровує байти у режимі OFB
     * симетрична операція process(process(data, iv), iv) == data.
     *
     * @param data вхідні байти
     * @param iv   ініціалізаційний вектор (16 байт)
     * @return результат
     */
    public byte[] process(byte[] data, byte[] iv) {
        if (iv.length != 16) {
            throw new IllegalArgumentException("IV має бути 16 байт");
        }

        byte[] result = new byte[data.length];
        byte[] currentBlock = iv.clone(); // поточний блок keystream (починаємо з IV)
        int done = 0;

        while (done < data.length) {
            // генеруємо наступний блок потоку O(i)
            currentBlock = cipher.encryptBlock(currentBlock);

            // XOR keystream із даними (до 16 байт за раз)
            int blockLen = Math.min(16, data.length - done);
            for (int i = 0; i < blockLen; i++) {
                result[done + i] = (byte) (data[done + i] ^ currentBlock[i]);
            }

            done += blockLen;
        }
        return result;
    }

    // обгортки для рядків

    /** шифрує рядок (UTF-8), повертає байти */
    public byte[] encrypt(String plaintext, byte[] iv) {
        return process(plaintext.getBytes(StandardCharsets.UTF_8), iv);
    }

    /** розшифровує байти, повертає рядок */
    public String decrypt(byte[] ciphertext, byte[] iv) {
        return new String(process(ciphertext, iv), StandardCharsets.UTF_8);
    }

    // допоміжні методи перетворення даних

    /** байти -> hex-рядок для виведення */
    public static String toHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b & 0xFF));
        }
        return sb.toString();
    }
}