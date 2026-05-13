import java.util.Scanner;

public class Main {

    public static void main(String[] args) {
        // класичний тестовий ключ AES 128-біт (16 байт)
        byte[] key = {
                0x2b, 0x7e, 0x15, 0x16, 0x28, (byte)0xae, (byte)0xd2, (byte)0xa6,
                (byte)0xab, (byte)0xf7, 0x15, (byte)0x88, 0x09, (byte)0xcf, 0x4f, 0x3c
        };
        // ініціалізаційний вектор IV (16 байт)
        byte[] iv = {
                0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
                0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f
        };

        Rijndael_OFB cipher = new Rijndael_OFB(key);

        System.out.println("  Rijndael (AES-128) in OFB mode");
        System.out.println("=".repeat(64));
        System.out.printf("  Key : %s%n", Rijndael_OFB.toHex(key));
        System.out.printf("  IV  : %s%n", Rijndael_OFB.toHex(iv));
        System.out.println();

        // тест 1: короткий рядок (менше 1 блоку = 16 байт)
        runTest(cipher, "Hello!", iv, "Test 1 (< 1 block)");

        // тест 2: рядок довший за 1 блок
        runTest(cipher, "Today is a beautiful sunny day in the city.", iv, "Test 2 (> 1 block)");

        // тест 3: той самий текст з іншим iv
        System.out.println("  Test 3 - IV impact:");
        byte[] zeroIv = new byte[16]; // масив нулів
        byte[] enc1 = cipher.encrypt("Hello AES!", iv);
        byte[] enc2 = cipher.encrypt("Hello AES!", zeroIv);
        System.out.println("    Original IV      : " + Rijndael_OFB.toHex(enc1));
        System.out.println("    Zero IV          : " + Rijndael_OFB.toHex(enc2));
        System.out.println("    Different results: " +
                !Rijndael_OFB.toHex(enc1).equals(Rijndael_OFB.toHex(enc2)));
        System.out.println();

        // iнтерактивний режим
        System.out.println("=".repeat(64));
        System.out.print("  Text to encrypt: ");
        Scanner scanner = new Scanner(System.in);
        String input = scanner.nextLine();
        byte[] encrypted = cipher.encrypt(input, iv);
        System.out.println("  Encrypted : " + Rijndael_OFB.toHex(encrypted));
        System.out.println("  Decrypted : " + cipher.decrypt(encrypted, iv));
        scanner.close();
    }

    private static void runTest(Rijndael_OFB cipher, String text, byte[] iv, String label) {
        byte[] enc = cipher.encrypt(text, iv);
        String dec = cipher.decrypt(enc, iv);
        System.out.println("  " + label + ":");
        System.out.println("    Plaintext : " + text);
        System.out.println("    Encrypted : " + Rijndael_OFB.toHex(enc));
        System.out.println("    Decrypted : " + dec);
        System.out.println("    OK        : " + text.equals(dec));
        System.out.println();
    }
}