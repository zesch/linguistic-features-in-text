package org.lift.features.api;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Semaphore;

import org.lift.features.util.FeatureUtil;


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
			escaped = FeatureUtil.escapeFeatureName(rawName);
			mapping.put(rawName, escaped);
			createLock.release();
		} catch (InterruptedException e) {
			throw new LiftFeatureExtrationException(e);
		}

		return escaped;
	}
}
