import numpy as np

class NoseConeGenerator:
    """Generates aerodynamic nose cone geometries based on analytical mathematical profiles."""
    
    def __init__(self, length: float = 0.5, base_radius: float = 0.05, num_points: int = 100):
        self.L = length
        self.R = base_radius
        self.n = num_points
        self.x = np.linspace(0, self.L, self.n)

    def sears_haack(self):
        """Sears-Haack profile: Minimizes wave drag for a given length and volume."""
        theta = np.arccos(1 - (2 * self.x / self.L))
        y = self.R * np.sqrt((theta - (np.sin(2 * theta) / 2)) / np.pi)
        return self.x, y

    def von_karman(self):
        """Von Kármán profile: Minimizes wave drag for a given length and base diameter."""
        theta = np.arccos(1 - (2 * self.x / self.L))
        y = self.R * np.sqrt((theta - (np.sin(2 * theta) / 2) + (1/3)*(np.sin(theta)**3)) / np.pi)
        return self.x, y

    def ogive(self):
        """Tangent Ogive profile."""
        rho = (self.R**2 + self.L**2) / (2 * self.R)
        y = np.sqrt(rho**2 - (self.L - self.x)**2) + self.R - rho
        return self.x, np.maximum(y, 0)

    def parabolic(self, K: float = 0.5):
        """Parabolic series nose cone."""
        y = self.R * ((2 * (self.x / self.L) - K * (self.x / self.L)**2) / (2 - K))
        return self.x, y
