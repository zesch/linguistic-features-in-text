package org.lift.features.util;

import java.util.Set;

import org.lift.features.api.Feature;
import org.junit.Assert;

public class FeatureTestUtil {


    /**
     * Shortcut for JUnit assert that test whether a feature has the correct name and value
     * 
     * @param expectedName
     *            expected
     * @param expectedValue
     *            actual
     * @param actualFeature
     *            feature
     */
    public static void assertFeature(String expectedName, Object expectedValue,
            Feature actualFeature)
    {
        Assert.assertNotNull(actualFeature);
        Assert.assertEquals(expectedName, actualFeature.getName());
        Assert.assertEquals(expectedValue, actualFeature.getValue());
    }

    /**
     * Shortcut for JUnit assert that test whether a feature has the correct name and double value
     * (compared using the epsilon)
     * 
     * @param expectedName
     *            expected
     * @param expectedValue
     *            actual
     * @param actualFeature
     *            feature
     * @param epsilon
     *            epsilon
     */
    public static void assertFeature(String expectedName, double expectedValue,
            Feature actualFeature, double epsilon)
    {
        Assert.assertNotNull(actualFeature);
        Assert.assertEquals(expectedName, actualFeature.getName());
        Assert.assertEquals(expectedValue, (Double) actualFeature.getValue(), epsilon);
    }

    /**
     * 
     * @param expectedName
     *            expected
     * @param expectedValue
     *            actual
     * @param features
     *            feature
     * @param epsilon
     *            epsilon
     */
    public static void assertFeatures(String expectedName, double expectedValue,
            Set<Feature> features, double epsilon)
    {
        Assert.assertNotNull(features);
        boolean found = false;
        for (Feature f : features) {
            if (f.getName().equals(expectedName)) {
                found = true;
                Assert.assertEquals(expectedValue, (Double) f.getValue(), epsilon);
            }
        }
        Assert.assertTrue(found);
    }

    /**
     * 
     * @param expectedName
     *            expected
     * @param expectedValue
     *            actual
     * @param features
     *            features
     */
    public static void assertFeatures(String expectedName, int expectedValue, Set<Feature> features)
    {
        Assert.assertNotNull(features);
        boolean found = false;
        for (Feature f : features) {
            if (f.getName().equals(expectedName)) {
                found = true;
                Assert.assertEquals(expectedValue, (int) f.getValue());
            }
        }
        Assert.assertTrue(found);
    }
}
