import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("\nGenerating Schnorr parameters (512 bits)...");
        Schnorr schnorr = new Schnorr(512);
        System.out.println("The keys and parameters have been successfully generated.");

        System.out.print("Enter the text for the caption: ");
        String text = scanner.nextLine();

        // Підписання
        Schnorr.Signature signature = schnorr.sign(text);
        System.out.println("\nElectronic signature:");
        System.out.println("e = " + signature.e.toString(16));
        System.out.println("s = " + signature.s.toString(16));

        // Верифікація правильного тексту
        boolean isValid = schnorr.verify(text, signature);
        System.out.println("\nSignature verification result for the original text: " + (isValid ? "Valid" : "Invalid"));

        System.out.println("\nAdding the number 1 to the text ");
        // Демонстрація захисту від підміни (верифікація зміненого тексту)
        String tamperedText = text + "1";
        boolean isTamperedValid = schnorr.verify(tamperedText, signature);
        System.out.println("Signature verification result for the modified text: " + (isTamperedValid ? "Valid" : "Invalid"));

        scanner.close();
    }
}