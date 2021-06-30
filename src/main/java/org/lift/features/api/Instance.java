package org.lift.features.api;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Comparator;
import java.util.List;

import org.apache.commons.lang3.StringUtils;

/**
 * Internal representation of an instance.
 *
 */
public class Instance
{
    private List<Feature> features;
    private List<String> outcomes;
    private double weight;
    private int sequenceId;
    private int sequencePosition;
    private int jcasId; // id of the jcas for which this instance was created

    public Instance()
    {
        this.features = new ArrayList<Feature>();
        this.outcomes = new ArrayList<String>();
    }

    public Instance(Collection<Feature> features, String outcome)
    {
        this.features = new ArrayList<Feature>(features);
        this.features.sort(getComparator());
        this.outcomes = new ArrayList<String>();
        this.outcomes.add(outcome.intern());
    }

    public Instance(Collection<Feature> features, String... outcomes)
    {
        this.features = new ArrayList<Feature>(features);
        this.features.sort(getComparator());
        this.outcomes = Arrays.asList(outcomes);
    }

    public Instance(Collection<Feature> features, List<String> outcomes)
    {
        this.features = new ArrayList<Feature>(features);
        this.outcomes = outcomes;
    }

    public void setOutcomes(Collection<String> outcomes)
    {
        this.outcomes.clear();
        this.outcomes.addAll(outcomes);
    }

    public void addFeature(Feature feature)
    {
        features.add(feature);
        features.sort(getComparator());
    }

    public void addFeatures(Collection<Feature> featureCollection)
    {
        features.addAll(featureCollection);
        features.sort(getComparator());
    }

    public String getOutcome()
    {
        if (outcomes.size() > 0) {
            return outcomes.get(0);
        }
        return null;
    }

    public List<String> getOutcomes()
    {
        return this.outcomes;
    }

    public void setOutcomes(String... outcomes)
    {
        this.outcomes.clear();
        this.outcomes.addAll(Arrays.asList(outcomes));
    }

    public double getWeight()
    {
        return this.weight;
    }

    public void setWeight(double weight)
    {
        this.weight = weight;
    }

    public void setJcasId(int id)
    {
        this.jcasId = id;
    }

    public int getJcasId()
    {
        return this.jcasId;
    }

    public Collection<Feature> getFeatures()
    {
        return features;
    }

    public void setFeatures(Collection<Feature> featureSet)
    {
        features = new ArrayList<Feature>(featureSet);
        features.sort(getComparator());
    }

    /**
     * @return The id of the sequence this instance is part of. 0 if not part of any sequence.
     */
    public int getSequenceId()
    {
        return sequenceId;
    }

    public void setSequenceId(int sequenceId)
    {
        this.sequenceId = sequenceId;
    }

    public int getSequencePosition()
    {
        return sequencePosition;
    }

    public void setSequencePosition(int sequencePosition)
    {
        this.sequencePosition = sequencePosition;
    }

    @Override
    public String toString()
    {
        StringBuilder sb = new StringBuilder();
        sb.append(jcasId);
        sb.append("-");
        sb.append(sequenceId);
        sb.append(" - ");
        sb.append(sequencePosition);
        sb.append("\n");
        for (Feature feature : getFeatures()) {
            sb.append(feature);
            sb.append("\n");
        }
        sb.append(StringUtils.join(outcomes, "-"));
        return sb.toString();
    }

    private Comparator<Feature> getComparator()
    {
        return new Comparator<Feature>()
        {
            public int compare(Feature o1, Feature o2)
            {
                return o1.name.compareTo(o2.name);
            }
        };
    }

}
