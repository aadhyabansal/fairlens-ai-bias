import pandas as pd
from app.schemas.audit import AuditRequest

min_subgrp_size=30

class ValidationError(Exception):
    "Raised when a dataset/request cannot be safely audited"
    pass

def load_and_validate(request: AuditRequest):

    warnings : list[str] =[]

    df=pd.read_csv(request.dataset_path)

    #1st Exception : target column not found
    if request.target_column not in df.columns:
        raise ValidationError(
            f"Target column {request.target_column} not found"
            f"Available columns: {df.columns}"
        )
    
    # 2nd exception : target column not binary
    unique_cols= df[request.target_column].dropna().unique();
    if len(unique_cols)!=2:
        raise ValidationError(
            f"Target column must be binary"
            f"{len(unique_cols)} unique columns found : {unique_cols}"
        )

    # 3rd exception : every sensitive attribute not found
    for attr in request.sensitive_attributes:
        if attr not in df.columns:
            raise ValidationError(
                f"Sensitive attribute {attr} not found"
                f"Available columns: {list(df.columns)}"
            )
        
    #4th exception : subgroup size
    for attr in request.sensitive_attributes:
        value_counts= df[attr].value_counts()
        small_groups= value_counts[value_counts<min_subgrp_size]

        if len(small_groups) == len(value_counts):
            raise ValidationError(
                f"All subgroups for '{attr}' have fewer than {min_subgrp_size} samples. Cannot compute reliable metrics."
            )

        for group_name, count in small_groups.items():
            warnings.append(
                f"'{attr}={group_name}' has only {count} samples (below {min_subgrp_size}) — metrics for this subgroup may be unreliable."
            )
    
    # overall size of dataset
    if len(df) < 100:
        warnings.append(
            f"Dataset has only {len(df)} rows total — "
            f"results should be treated as preliminary."
        )

    return df, warnings