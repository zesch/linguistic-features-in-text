package org.lift.api;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Semaphore;

import org.apache.commons.lang3.StringUtils;


/**
 * Escapes features to ensure that they do not contain non-standard characters.
 * This class is thread-safe if used as static instance.
 */
public class FeatureNameEscaper {

	private Map<String, String> mapping = new HashMap<>();
	private Semaphore createLock = new Semaphore(1);

	/**
	 * Escapes feature names. The substitution is synchronized by
	 * a @link{java.util.concurrent.Semaphore} if used by multiple threads.
	 * 
	 * @param rawName
	 *            the unescaped name of the feature
	 * @return the escaped name of the feature, will be identical to the input
	 *         if no characters are found that require escaping
	 * @throws TextClassificationException
	 *             in case of an error
	 */
	public String escape(String rawName) 
			throws LiftFeatureExtrationException 
	{

		if (mapping.containsKey(rawName)) {
			return mapping.get(rawName);
		}

		String escaped = rawName;
		try {
			createLock.acquire();
			escaped = escapeFeatureName(rawName);
			mapping.put(rawName, escaped);
			createLock.release();
		} catch (InterruptedException e) {
			throw new LiftFeatureExtrationException(e);
		}

		return escaped;
	}
	
    /*
     * Escapes the names, as Weka does not seem to like special characters in attribute names.
     */
    public static String escapeFeatureName(String name)
    {
        // TODO Issue 120: improve the escaping
        // the fix was necessary due to Issue 32
        // http://code.google.com/p/dkpro-tc/issues/detail?id=32
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < name.length(); i++) {
            String c = name.substring(i, i + 1);
            if (StringUtils.isAlphanumeric(c) || c.equals("_")) {
                sb.append(c);
            }
            else {
                sb.append("u");
                sb.append(c.codePointAt(0));
            }
        }
        return sb.toString();
    }
}
