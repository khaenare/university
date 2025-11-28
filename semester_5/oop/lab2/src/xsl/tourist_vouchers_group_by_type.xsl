<?xml version="1.0" encoding="UTF-8"?>

<!--
    XSLT для групування туристичних путівок за типом.
    Вихідна структура:
    <tourist_vouchers_grouped>
        <WEEKEND>...</WEEKEND>
        <EXCURSION>...</EXCURSION>
        <REST>...</REST>
        <PILGRIMAGE>...</PILGRIMAGE>
    </tourist_vouchers_grouped>
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">
    <xsl:output method="xml" indent="yes" encoding="UTF-8"/>

    <!-- Головний шаблон: спрацьовує на кореневий елемент <tourist_vouchers> -->
    <xsl:template match="/tourist_vouchers">
        <tourist_vouchers_grouped>

            <WEEKEND>
                <!-- Всі путівки типу WEEKEND -->
                <xsl:apply-templates select="tourist_voucher[type='WEEKEND']"/>
            </WEEKEND>

            <EXCURSION>
                <!-- Всі путівки типу EXCURSION -->
                <xsl:apply-templates select="tourist_voucher[type='EXCURSION']"/>
            </EXCURSION>

            <REST>
                <!-- Всі путівки типу REST -->
                <xsl:apply-templates select="tourist_voucher[type='REST']"/>
            </REST>

            <PILGRIMAGE>
                <!-- Всі путівки типу PILGRIMAGE -->
                <xsl:apply-templates select="tourist_voucher[type='PILGRIMAGE']"/>
            </PILGRIMAGE>

        </tourist_vouchers_grouped>
    </xsl:template>

    <!--
        Шаблон для копіювання окремої путівки.
        Ми створюємо новий елемент <tourist_voucher> і просто копіюємо
        всі атрибути та дочірні елементи (id, type, country, hotel, cost тощо).
    -->
    <xsl:template match="tourist_voucher">
        <tourist_voucher>
            <xsl:copy-of select="@*|*"/>
        </tourist_voucher>
    </xsl:template>

</xsl:stylesheet>
