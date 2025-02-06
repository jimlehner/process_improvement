import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
import pandas as pd
import warnings

def limit_chart(df, values, x_labels, USL, LSL, target, title='Limit Chart', y_label='Value', 
                     x_label='', figsize=(15,3), round_value=4, dpi=300, show_limit_values=True,
               tickinterval=5, rotate_labels=0):
    
    """
    Generate a specifcation limit chart plot and calculate relevant parameters.

    Parameters:
    -----------
    df : pandas.DataFrame
        Input dataframe containing the data.
    values : str or list of str
        Column name(s) in `df` that contain the values to be plotted.
    x_labels : str or list of str
        Column name(s) in `df` that provide labels for the x-axis.
    target : float
        Target value for the process.
    USL : float
        Upper Specification Limit.
    LSL : float
        Lower Specification Limit.
    title : str, optional
        Title of the plot (default is 'Limit Chart').
    y_label : str, optional
        Label for the y-axis (default is 'Value').
    x_label : str, optional
        Label for the x-axis (default is '').
    figsize : tuple, optional
        Figure size in inches (width, height) (default is (15, 3)).
    round_value : int, optional
        Number of decimal places to round mean and PBC parameters (default is 4).
    dpi : int, optional
        Dots per inch for figure resolution (default is 300).
    show_limit_values : bool, optional
        If True, displays numerical values for process limits. Default is True.

    Returns:
    --------
    pandas.DataFrame
        DataFrame summarizing the calculated PBC parameters including Mean, Target, Mean to Target Delta,
        Upper Specification Limit (USL), Lower Specification Limit (LSL), Specification Limit Range (SLR),
        Number of Values, Number of Values Outside Specification Limits (# Outside Spec), and
        Percentage of Values Outside Specification Limits (% Outside Spec).
    """
    # Validate input types
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")
    if not isinstance(values, (str, list)):
        raise TypeError("values must be a string or a list of strings.")
    if not isinstance(x_labels, (str, list)):
        raise TypeError("x_labels must be a string or a list of strings.")
    if not all(isinstance(i, (int, float)) for i in [USL, LSL, target]):
        raise TypeError("USL, LSL, and target must be numeric values.")
    
    # Check if columns exist in df
    missing_cols = [col for col in ([values] if isinstance(values, str) else values) if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in DataFrame: {missing_cols}")
    if x_labels not in df.columns:
        raise ValueError(f"x_labels column '{x_labels}' not found in DataFrame.")
    
    # Disaggregate the dataframe 
    data = df[values]
    labels = df[x_labels]
    
    # Check if data is empty
    if data.empty:
        raise ValueError("The data column is empty. Nothing to plot.")
    
    # Values in dataset
    data_length = len(data)
    if data_length == 0:
        raise ValueError("The data column is empty. Nothing to plot.")
    
    # Calculate the mean
    mean = data.mean()
    mean_to_target_delta = target - mean

    # Calculate specification limit range (SLR)
    SLR = USL - LSL

    # Masking parameters for values outside spec limits
    outside_USL = np.sum(data > USL)
    outside_LSL = np.sum(data < LSL)
    outside_spec = round(outside_USL + outside_LSL,round_value)
    percent_outside_spec = round((outside_spec/data_length)*100,round_value)

    # Create masking parameters for values greater than and less than the process limits on X-chart
    upper_lim = np.ma.masked_where(data < USL, data)
    lower_lim = np.ma.masked_where(data > LSL, data)
    # Create masking parameters for values greater than URL on mR-chart
    usl_greater = np.ma.masked_where(data < USL, data)
    usl_less = np.ma.masked_where(data > USL, data)

    # Create list of tuples that specify value and color for mean, AmR, UPL, LPL, and URL
    chart_lines = [(mean,'black'), (USL,'grey'), (LSL,'grey')]
    # Create list of tuples with y-coordinate and labels for x-chart process limits and centerline 
    chart_labels = [(USL,USL),(LSL,LSL),(mean,mean)]

    # Generate the X-chart
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # Plot data 
    ax.plot(labels, data, marker='o')

    # Add masking parameters to color values outside process limits
    ax.plot(labels, lower_lim, marker='o', ls='none', color='tab:red',
            markeredgecolor='black', markersize=9)
    ax.plot(labels, upper_lim, marker='o', ls='none', color='tab:red',
            markeredgecolor='black', markersize=9)

    # Add text labels for limits and centerline
    bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="grey", lw=1)
    bbox_props_centerlines = dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=1)

    # Conditionally show limit values
    if show_limit_values:
        limit_labels = [USL, LSL, target]
    else:
        limit_labels = ['USL', 'LSL', 'Target']

    # Get xlimit
    xlimit = ax.get_xlim()[1]

    annotations = [
        (limit_labels[0], xlimit, USL, ax),  # UPL annotation on ax[0]
        (limit_labels[1], xlimit, LSL, ax),  # LPL annotation on ax[0]
        (limit_labels[2], xlimit, target, ax)
    ]

    # Add annotations
    for label, x_pos, y_pos, axis in annotations:
        axis.annotate(label,
                      xy=(x_pos, y_pos),
                      ha='center',
                      va='center',
                      bbox=dict(facecolor='white', boxstyle='round'))

    # Add centerline and process limits 
    for value, color in chart_lines:
        plt.axhline(value, ls='--', c=color)
        
    tick_positions = np.arange(0, len(labels), tickinterval)
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(labels.iloc[tick_positions], rotation=rotate_labels, ha='center')

    # Specify spine visibility 
    ax.spines[['top','right']].set_visible(False)
    ax.spines[['left','bottom']].set_alpha(0.5)

    # Specify axis labels and title
    plt.xlabel(x_label,fontsize=12)
    plt.ylabel(y_label, fontsize=12)
    plt.title(title, fontsize=14)

    # Show plot
    plt.show()

    # Create list of PBC paramters
    chart_params = ['Mean','Target','Mean to Tar. Delta','USL','LSL',
                    'Spec Limit Range','# of Values','# Outside Spec', '% Outside Spec']
    chart_type = ['Limit Chart']*len(chart_params)
    chart_values = [round(x,round_value) for x in [mean, target, mean_to_target_delta, USL, LSL, SLR, 
                    data_length, outside_spec, percent_outside_spec]]
    # Create df for PBC parameters
    results_df = pd.DataFrame()
    results_df['Chart'] = pd.Series(chart_type)
    results_df['Parameters'] = pd.Series(chart_params)
    results_df['Values'] = pd.Series(chart_values)

    return results_df