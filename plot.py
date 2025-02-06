import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
import matplotlib.image as mpimg
import os


def plot_grid(x_dim: int, y_dim: int):
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 6))

    # Set dark background
    # ax.set_facecolor("black")
    # fig.patch.set_facecolor("black")

    # Define grid,s
    x_lines = np.arange(-0.5, x_dim + 0.5, 1.0)
    y_lines = np.arange(-0.5, y_dim + 0.5, 1.0)

    for x in x_lines:
        ax.axvline(x=x, color="white", linewidth=1, zorder=2)
    for y in y_lines:
        ax.axhline(y=y, color="white", linewidth=1, zorder=2)

    ax.set_xticks(range(x_dim + 1))
    ax.set_yticks(range(y_dim + 1))
    ax.set_aspect("equal")

    # Add rectangles with lower zorder
    red_rect = patches.Rectangle((-0.5, y_dim / 2 - 0.5), x_dim, y_dim / 2, facecolor="red", alpha=0.4, zorder=1)
    blue_rect = patches.Rectangle((-0.5, -0.5), x_dim, y_dim / 2, facecolor="blue", alpha=0.4, zorder=1)
    ax.add_patch(red_rect)
    ax.add_patch(blue_rect)

    ax.set_xlim(-0.5, x_dim - 0.5)
    ax.set_ylim(-0.5, y_dim - 0.5)
    return fig, ax


def plot_asset(ax, asset):
    img_path = os.path.join(
        "/home/nick/repos/personal/ICBM-Game/asset_images", asset["team"] + "-" + f"{asset['type']}" + ".png"
    )
    try:
        img = mpimg.imread(str(img_path))
        x, y = asset["position"]
        extent = [x - 0.4, x + 0.4, y - 0.5, y + 0.5]
        # Set higher zorder for images
        ax.imshow(img, extent=extent, zorder=3)

        # Draw the "circle" (diamond) around the asset based on its visibility range
        visibility_range = asset["visibility_range"]

        if visibility_range == 0:
            return ax

        # Generate the points within the Manhattan distance (the "polygon")
        for dx in range(-visibility_range, visibility_range + 1):
            for dy in range(-visibility_range, visibility_range + 1):
                if abs(dx) + abs(dy) <= visibility_range:  # Manhattan distance condition
                    # Plot a rectangle to cover the grid squares
                    ax.add_patch(
                        patches.Rectangle(
                            (x + dx - 0.5, y + dy - 0.5), 1, 1, facecolor="white", alpha=0.4, edgecolor="white", zorder=1
                        )
                    )
    except FileNotFoundError:
        print(f"Warning: Image not found for {asset['type']}")
        ax.plot(x, y, "wx", zorder=3)

    return ax


def plot_assets_grid(fig, ax, assets, plot_kinematics=False):

    # Plot static, then dynamic so we don't plot every asset in a launch site
    launch_site_locations = []
    for asset in assets:
        if asset["speed"] == 0:
            ax = plot_asset(ax, asset)
        if asset["type"] == "launch_site":
            launch_site_locations.append(asset["position"])

    for asset in assets:
        if asset["speed"] > 0 and asset:
            # Skip anyting currently co-located with a launch site
            if asset["position"] in launch_site_locations:
                continue

            # Lines for reachable positions can make it cluttered, have this configurable
            if plot_kinematics:

                x, y = asset["position"]
                speed = asset["speed"]
                movement_range = asset["movement_range"]

                # Cap speed at movement range to prevent jumping over the max range
                if speed > movement_range:
                    speed = movement_range

                # Draw speed circle vertices
                for dx in range(-speed, speed + 1):
                    for dy in range(-speed + abs(dx), speed - abs(dx) + 1):
                        if abs(dx) + abs(dy) < speed:
                            continue
                        ax.plot([x, x + dx], [y, y + dy], "w-", linewidth=2, alpha=0.5, zorder=2)

                # Draw range lines
                for dx in range(-movement_range, movement_range + 1):
                    for dy in range(-movement_range + abs(dx), movement_range - abs(dx) + 1):
                        if abs(dx) + abs(dy) < movement_range:
                            continue
                        ax.plot([x, x + dx], [y, y + dy], "w--", linewidth=1, alpha=0.3, zorder=2)

            ax = plot_asset(ax, asset)

    return fig, ax


# Example usage
if __name__ == "__main__":
    x_dim = 30
    y_dim = 20

    fig, ax = plot_grid(x_dim=x_dim, y_dim=y_dim)

    assets = [
        {"type": "citadel", "team": "blue", "position": [0, 0], "visibility_range": 2, "speed": 0, "movement_range": 0},
        {"type": "icbm", "team": "blue", "position": [2, 2], "visibility_range": 0, "speed": 4, "movement_range": 4},
        {"type": "icbm", "team": "blue", "position": [4, 2], "visibility_range": 0, "speed": 4, "movement_range": 6},
        {"type": "launch_site", "team": "blue", "position": [4, 2], "visibility_range": 2, "speed": 0, "movement_range": 0},
        {
            "type": "long-range-interceptor",
            "team": "blue",
            "position": [12, 6],
            "visibility_range": 0,
            "speed": 6,
            "movement_range": 6,
        },
        {
            "type": "short-range-interceptor",
            "team": "blue",
            "position": [9, 8],
            "visibility_range": 0,
            "speed": 6,
            "movement_range": 2,
        },
        {"type": "icbm", "team": "red", "position": [2, 8], "visibility_range": 0, "speed": 4, "movement_range": 10},
        {"type": "launch_site", "team": "red", "position": [4, 8], "visibility_range": 2, "speed": 0, "movement_range": 0},
        {"type": "citadel", "team": "red", "position": [17, 14], "visibility_range": 2, "speed": 0, "movement_range": 0},
        {
            "type": "long-range-radar",
            "team": "red",
            "position": [14, 5],
            "visibility_range": 4,
            "speed": 0,
            "movement_range": 0,
        },
        {"type": "artillery", "team": "red", "position": [13, 3], "visibility_range": 0, "speed": 2, "movement_range": 3},
        {
            "type": "short-range-interceptor",
            "team": "red",
            "position": [19, 6],
            "visibility_range": 0,
            "speed": 4,
            "movement_range": 4,
        },
        {
            "type": "short-range-radar",
            "team": "red",
            "position": [12, 12],
            "visibility_range": 2,
            "speed": 0,
            "movement_range": 0,
        },
        {"type": "cruise-missile", "team": "red", "position": [9, 12], "visibility_range": 0, "speed": 3, "movement_range": 8},
        {"type": "recon-plane", "team": "red", "position": [28, 4], "visibility_range": 0, "speed": 3, "movement_range": 8},
    ]

    fig, ax = plot_assets_grid(fig, ax, assets, plot_kinematics=False)

    plt.show()
