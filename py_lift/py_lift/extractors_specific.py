from cassis import Cas
from collections import Counter
from py_lift.extractors import FEL_BaseExtractor

class FE_FreqBandRatios(FEL_BaseExtractor):
    """Extractor that computes the ratio of frequency bands per token. 
    Assumes that 'org.lift.type.Frequency' structure annotations are present in the CAS."""
    
    def __init__(self):
        super().__init__()
    
    def extract(self, cas: Cas) -> bool:
        F = self.ts.get_type("FeatureAnnotationNumeric")
        
        # Count frequency bands
        band_counts = Counter(
            freq.frequencyBand 
            for freq in cas.select('org.lift.type.Frequency')
        )
        
        # Handle empty case
        total = sum(band_counts.values())
        if total == 0:
            return True  # or False, depending on your requirements
        
        # Define feature mappings
        feature_mappings = {
            'f1': 'Freq_Ratio_F1_PER_Token',
            'f2': 'Freq_Ratio_F2_PER_Token',
            'f3': 'Freq_Ratio_F3_PER_Token',
            'f4': 'Freq_Ratio_F4_PER_Token',
            'f5': 'Freq_Ratio_F5_PER_Token',
            'f6': 'Freq_Ratio_F6_PER_Token',
            'f7': 'Freq_Ratio_F7_PER_Token',
            'oov': 'Freq_Ratio_OOV_PER_Token'
        }
        
        # Create and add features
        for band, feature_name in feature_mappings.items():
            ratio = band_counts.get(band, 0) / total
            feature = F(name=feature_name, value=ratio, begin=0, end=0)
            cas.add(feature)

        self._print_distribution(band_counts, total)
        
        return True

    def _print_distribution(self, band_counts: dict, total: int):
        """Print frequency band distribution as stacked bar chart."""
        bands = list(sorted(band_counts.keys()))
        
        # Calculate ratios
        ratios = {band: band_counts.get(band, 0) / total for band in bands}
        total_ratio = sum(ratios.values())
        
        print(f"\n{'='*70}")
        print(f"Frequency Band Distribution (total: {total}, sum: {total_ratio:.4f})")
        print('='*70)
        
        # Individual bars
        for band in bands:
            ratio = ratios[band]
            percentage = ratio * 100
            bar_length = int(ratio * 50)
            bar = '█' * bar_length
            count = band_counts.get(band, 0)
            print(f"{band:>4}: {bar:<50} {percentage:5.1f}% ({count:>4})")
        
        print('='*70)