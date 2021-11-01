package org.lift.higherorder.genuine;

import java.util.Collection;
import java.util.HashSet;
import java.util.Set;

import org.apache.uima.cas.FeatureStructure;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FeatureExtractor_ImplBase;

import de.tudarmstadt.ukp.dkpro.core.api.syntax.type.PennTree;
import de.tudarmstadt.ukp.dkpro.core.api.syntax.type.constituent.Constituent;

public class FE_SyntaxTreeDepth extends FeatureExtractor_ImplBase {
	
	public static final String AVG_SYNTAX_TREE_DEPTH = "syntaxTreeDepthAvg";
	public static final String TOTAL_SYNTAX_TREE_DEPTH = "syntaxTreeDepthMax";
	
	private String languageCode;

	public FE_SyntaxTreeDepth(String languageCode) {
		super("SyntaxTreeDepth", FE_SyntaxTreeDepth.class.getName());
		this.languageCode = languageCode;
	}

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		double totalTreeDepth = 0;
		Collection<PennTree> trees = JCasUtil.select(jcas, PennTree.class);
		// check every penntree for the root element and calculate the depth of the tree from there
		for (PennTree tree : trees) {
			Collection<Constituent> constituents = JCasUtil.selectCovered(
					Constituent.class, tree);
			for (Constituent constituent : constituents) {
				if (constituent.getConstituentType().equals("ROOT")) {
					String rootText = constituent.getCoveredText().replaceAll("\\s*\\p{Punct}+\\s*$", "");
					totalTreeDepth += depthOfTree(constituent,rootText);
				}
			}
		}
		//Normalization on total count of trees
		double avgTreeDepth = (double) totalTreeDepth / trees.size();

		Set<Feature> featList = new HashSet<Feature>();
		featList.add(new Feature(AVG_SYNTAX_TREE_DEPTH, avgTreeDepth, FeatureType.NUMERIC));
		featList.add(new Feature(TOTAL_SYNTAX_TREE_DEPTH, totalTreeDepth, FeatureType.NUMERIC));
		return featList;
	}
	
	public double depthOfTree(Constituent constituent,String rootText) {
		String type = constituent.getConstituentType();
		String text = constituent.getCoveredText().replaceAll("\\s*\\p{Punct}+\\s*$", "");
		//Filter the constituent type S and PSEUDO(potential non-tree structures in German)
		//Because they duplicate the ROOT
		boolean duplicate=false;
		//Filter the constituent type S in English, because it will cause duplication
		if(languageCode.equals("en")){
			duplicate = type.equals("S");
		//Filter the constituent type S, which is the duplication of ROOT
		//Filter the constituent typ PSEUDO(potential non-tree structures in German)
		} else if(languageCode.equals("de")){
			duplicate = (type.equals("S")&&text.equals(rootText))||type.equals("PSEUDO");
		} else{
			System.err.println("Illegal Language Setting");
		}
		if(duplicate){
			return maxDepthOfSubtree(constituent.getChildren().toArray(),rootText);
		} else{
			return 1+maxDepthOfSubtree(constituent.getChildren().toArray(),rootText);
		}
	}
	
	private double maxDepthOfSubtree(FeatureStructure[] children,String rootText) {
		double max = 0;
		for (FeatureStructure child : children) {
			if (!child.getType().getShortName().equals("Token")) {
				double temp = depthOfTree((Constituent) child,rootText);
				if (max < temp)
					max = temp;
			}
		}
		return max;
	}

}
