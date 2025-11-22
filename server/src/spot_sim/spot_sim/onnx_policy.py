# SPDX-FileCopyrightText: 2026 Kane Li <kaneli200456@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
ONNX Runtime implementation of the Spot policy network.
Provides faster inference than PyTorch with smaller binary size.

Architecture: 48 -> [512->ELU] -> [256->ELU] -> [128->ELU] -> 12
"""

import numpy as np
import os
import onnxruntime as ort


class ONNXSpotPolicy:
    """
    ONNX Runtime implementation of the Spot policy neural network.
    Provides faster CPU inference compared to PyTorch.
    """
    
    def __init__(self, onnx_path: str):
        """
        Initialize the policy by loading the ONNX model.
        
        Args:
            onnx_path: Path to the .onnx model file
        """
        if not os.path.exists(onnx_path):
            raise FileNotFoundError(
                f"ONNX model file not found: {onnx_path}\n"
                "Please export the model to ONNX format first."
            )
        
        # Create ONNX Runtime session with CPU provider
        self.session = ort.InferenceSession(
            onnx_path,
            providers=['CPUExecutionProvider']
        )
        
        # Get input/output names
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
    
    def forward(self, observation: np.ndarray) -> np.ndarray:
        """
        Perform forward pass through the network.
        
        Args:
            observation: Input observation array of shape (48,) or (1, 48)
        
        Returns:
            Action array of shape (12,)
        """
        # Ensure input is 2D: (batch_size, 48) and float32
        x = observation.reshape(1, -1)
        
        # Run inference
        outputs = self.session.run(
            [self.output_name],
            {self.input_name: x}
        )
        
        # Return as 1D array
        return outputs[0].squeeze(0)
    
    def __call__(self, observation: np.ndarray) -> np.ndarray:
        """
        Make the policy callable like the PyTorch version.
        
        Args:
            observation: Input observation array of shape (48,) or (1, 48)
        
        Returns:
            Action array of shape (12,)
        """
        return self.forward(observation)
