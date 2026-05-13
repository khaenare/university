import java.math.BigInteger;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.nio.charset.StandardCharsets;

public class Schnorr {

    // Клас для зберігання структури електронного підпису
    public static class Signature {
        public final BigInteger e;
        public final BigInteger s;

        public Signature(BigInteger e, BigInteger s) {
            this.e = e;
            this.s = s;
        }
    }

    private final BigInteger p;
    private final BigInteger q;
    private final BigInteger g;
    private final BigInteger privateKey;
    private final BigInteger publicKey;
    private final SecureRandom random;

    // Генерація нових параметрів та ключів
    public Schnorr(int bitLength) {
        this.random = new SecureRandom();

        // 1. Генерація простого числа q (160 біт)
        this.q = new BigInteger(160, 100, random);

        // 2. Генерація простого числа p, такого що q є дільником p - 1
        BigInteger k = new BigInteger(bitLength - 160, random);
        k = k.clearBit(0); // Робимо парним, щоб p було непарним
        BigInteger pTemp;
        while (true) {
            pTemp = k.multiply(q).add(BigInteger.ONE);
            if (pTemp.isProbablePrime(100)) {
                break;
            }
            k = k.add(BigInteger.valueOf(2));
        }
        this.p = pTemp;

        // 3. Генерація генератора g підгрупи порядку q
        BigInteger gTemp;
        while (true) {
            BigInteger h = new BigInteger(p.bitLength() - 1, random);
            if (h.compareTo(BigInteger.ONE) <= 0) continue;

            gTemp = h.modPow(k, p);
            if (gTemp.compareTo(BigInteger.ONE) > 0) {
                break;
            }
        }
        this.g = gTemp;

        // 4. Генерація приватного (x) та публічного (y) ключів
        this.privateKey = generatePrivateKey();
        this.publicKey = g.modPow(privateKey, p);
    }

    // Генерація випадкового x в діапазоні (0, q)
    private BigInteger generatePrivateKey() {
        BigInteger key;
        do {
            key = new BigInteger(q.bitLength(), random).mod(q);
        } while (key.equals(BigInteger.ZERO));
        return key;
    }

    // Хешування повідомлення та числа r
    private BigInteger hash(byte[] message, BigInteger r) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            digest.update(message);
            digest.update(r.toByteArray());
            byte[] hashBytes = digest.digest();
            return new BigInteger(1, hashBytes);
        } catch (NoSuchAlgorithmException ex) {
            throw new RuntimeException("SHA-256 initialization error", ex);
        }
    }

    // Функція створення цифрового підпису
    public Signature sign(String messageText) {
        byte[] message = messageText.getBytes(StandardCharsets.UTF_8);

        BigInteger kVal;
        do {
            kVal = new BigInteger(q.bitLength(), random).mod(q);
        } while (kVal.equals(BigInteger.ZERO));

        // Обчислення r = g^k mod p
        BigInteger r = g.modPow(kVal, p);

        // Обчислення e = H(M || r)
        BigInteger e = hash(message, r);

        // Обчислення s = (k + x * e) mod q
        BigInteger s = kVal.add(privateKey.multiply(e)).mod(q);

        return new Signature(e, s);
    }

    // Функція перевірки цифрового підпису
    public boolean verify(String messageText, Signature sig) {
        byte[] message = messageText.getBytes(StandardCharsets.UTF_8);

        if (sig.s.compareTo(BigInteger.ZERO) < 0 || sig.s.compareTo(q) >= 0) {
            return false;
        }

        // Обчислення r' = (g^s * y^(-e)) mod p
        BigInteger yInv = publicKey.modPow(sig.e, p).modInverse(p);
        BigInteger rPrime = g.modPow(sig.s, p).multiply(yInv).mod(p);

        // Перевірка e == H(M || r')
        BigInteger ePrime = hash(message, rPrime);

        return sig.e.equals(ePrime);
    }
}