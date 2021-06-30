package org.lift.features.api;

/**
 * Exception thrown by DKPro TC components.
 */
public class LiftFeatureExtrationException
    extends Exception
{

    static final long serialVersionUID = 1L;

    /**
     * 
     */
    public LiftFeatureExtrationException()
    {
        super();
    }

    /**
     * @param txt
     */
    public LiftFeatureExtrationException(String txt)
    {
        super(txt);
    }

    /**
     * @param message
     * @param cause
     */
    public LiftFeatureExtrationException(String message, Throwable cause)
    {
        super(message, cause);
    }

    /**
     * @param cause
     */
    public LiftFeatureExtrationException(Throwable cause)
    {
        super(cause);
    }

}
