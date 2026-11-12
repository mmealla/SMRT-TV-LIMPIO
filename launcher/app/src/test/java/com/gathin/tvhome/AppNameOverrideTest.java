package com.gathin.tvhome;

import org.junit.Test;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

public class AppNameOverrideTest {

    @Test public void anEntryMapsItsPackageToItsOverride() {
        Map<String, String> m = Config.appOverrides(Collections.singletonList(
                "com.example.app=Mi nombre"));
        assertEquals("Mi nombre", m.get("com.example.app"));
    }

    @Test public void spacesAroundTheHalvesAreTrimmed() {
        assertEquals("Nombre", Config.appOverrides(Collections.singletonList(" a.pkg = Nombre ")).get("a.pkg"));
    }

    @Test public void entriesWithoutBothHalvesAreSkipped() {
        assertTrue(Config.appOverrides(Arrays.asList("a.pkg", "=Nombre", "a.pkg=", "")).isEmpty());
    }

    @Test public void aLaterEntryForAPackageWins() {
        assertEquals("segundo", Config.appOverrides(Arrays.asList("a.pkg=primero", "a.pkg=segundo")).get("a.pkg"));
    }

    @Test public void overrideTakesPrecedenceOverThemeAndAppLabel() {
        assertEquals("override", Cards.resolveAppLabel("override", "theme", "app", "card"));
    }

    @Test public void themeLabelWinsWhenNoOverride() {
        assertEquals("theme", Cards.resolveAppLabel("", "theme", "app", "card"));
        assertEquals("theme", Cards.resolveAppLabel(null, "theme", "app", "card"));
    }

    @Test public void appLabelWinsWhenNoOverrideOrTheme() {
        assertEquals("app", Cards.resolveAppLabel("", "", "app", "card"));
    }

    @Test public void cardLabelIsLastResort() {
        assertEquals("card", Cards.resolveAppLabel("", "", "", "card"));
    }

    @Test public void emptyOrSpacesOverrideDoesNotLeaveTileWithoutLabel() {
        // resolved raw is empty -> Cards.cleanLabel falls back to package name
        String resolved = Cards.resolveAppLabel("   ", "", "", "");
        assertEquals("com.example.app", Cards.cleanLabel(resolved, "com.example.app"));
    }

    @Test public void maxLengthIsHonoured() {
        StringBuilder longName = new StringBuilder();
        for (int i = 0; i < 60; i++) longName.append('a');
        String resolved = Cards.resolveAppLabel(longName.toString(), "", "", "");
        String cleaned = Cards.cleanLabel(resolved, "pkg");
        assertTrue(cleaned.length() <= 40);
    }

    @Test public void controlCharOrNewlineIsSanitized() {
        String resolved = Cards.resolveAppLabel("Linea\nDos", "", "", "");
        String cleaned = Cards.cleanLabel(resolved, "pkg");
        // newline must not survive into the label
        assertTrue(!cleaned.contains("\n"));
    }

    @Test public void roundTripEncodeDecode() {
        List<String> entries = Arrays.asList("com.example.app=Mi nombre");
        Map<String, String> parsed = Config.appOverrides(entries);
        assertEquals("Mi nombre", parsed.get("com.example.app"));
        // re-encode and re-parse yields the same value
        String encoded = "com.example.app=" + parsed.get("com.example.app");
        assertEquals("Mi nombre", Config.appOverrides(Collections.singletonList(encoded)).get("com.example.app"));
    }
}