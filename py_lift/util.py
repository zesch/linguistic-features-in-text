def resolve_annotation(annotation_path: str, feature_seperator='/') -> tuple[str, str]:
    if feature_seperator == '.':
        raise ValueError('Feature separator must not be "."')

    split = annotation_path.split(feature_seperator)

    if len(split) > 2:
        raise ValueError(f'Annotation Path is ill defined, as it contains multiple features, seperated by {feature_seperator}')

    # no feature in annotation path
    if len(split) == 1:
        return split[0], ''

    type_path, feature_path = split

    return type_path, feature_path