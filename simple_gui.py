import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QFileDialog)
from PyQt6.QtCore import Qt
import soundfile as sf
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class SimpleAudioProcessor:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
    
    def process_audio(self, audio):
        # Simple processing - just add some effects
        processed = audio * 0.8  # Reduce volume
        # Add slight echo
        echo = np.roll(audio, 4410)  # 0.1 second delay
        processed += echo * 0.3
        return np.clip(processed, -1.0, 1.0)

class WaveformVisualizer(FigureCanvas):
    def __init__(self, parent=None, width=5, height=2, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        fig.tight_layout()
        
    def plot_waveform(self, audio, sample_rate, title=""):
        self.axes.clear()
        time = np.arange(len(audio)) / sample_rate
        self.axes.plot(time, audio, linewidth=0.5)
        self.axes.set_xlabel('Time (s)')
        self.axes.set_ylabel('Amplitude')
        self.axes.set_title(title)
        self.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Audio Processor")
        self.setMinimumSize(800, 600)
        
        # Initialize variables
        self.audio_data = None
        self.sample_rate = None
        self.processor = SimpleAudioProcessor()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add upload button
        self.upload_button = QPushButton("Click to Upload Audio File")
        self.upload_button.setStyleSheet("""
            QPushButton {
                padding: 20px;
                font-size: 16px;
                background-color: #f0f0f0;
                border: 2px dashed #666;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #333;
            }
        """)
        self.upload_button.clicked.connect(self.select_input_file)
        layout.addWidget(self.upload_button)
        
        # Status label
        self.status_label = QLabel("Click the button to upload a WAV file")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Waveform visualizers
        self.waveform_original = WaveformVisualizer(self)
        layout.addWidget(self.waveform_original)
        
        self.waveform_processed = WaveformVisualizer(self)
        layout.addWidget(self.waveform_processed)
        
        # Process and Save buttons
        self.process_button = QPushButton("Process Audio")
        self.process_button.clicked.connect(self.process_audio)
        self.process_button.setEnabled(False)
        layout.addWidget(self.process_button)
        
        self.save_button = QPushButton("Save Processed Audio")
        self.save_button.clicked.connect(self.save_audio)
        self.save_button.setEnabled(False)
        layout.addWidget(self.save_button)
    
    def select_input_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "WAV Files (*.wav);;All Files (*.*)"
        )
        if file_name:
            try:
                self.audio_data, self.sample_rate = sf.read(file_name)
                self.status_label.setText(f"Loaded: {file_name}")
                self.waveform_original.plot_waveform(
                    self.audio_data, self.sample_rate, "Original Audio"
                )
                self.process_button.setEnabled(True)
            except Exception as e:
                self.status_label.setText(f"Error loading file: {str(e)}")
    
    def process_audio(self):
        if self.audio_data is None:
            return
            
        try:
            # Process audio
            self.status_label.setText("Processing audio...")
            processed_audio = self.processor.process_audio(self.audio_data)
            
            # Update visualization
            self.waveform_processed.plot_waveform(
                processed_audio, self.sample_rate, "Processed Audio"
            )
            
            # Enable save button
            self.save_button.setEnabled(True)
            self.processed_audio = processed_audio
            
            self.status_label.setText("Processing complete!")
            
        except Exception as e:
            self.status_label.setText(f"Error processing audio: {str(e)}")
    
    def save_audio(self):
        if not hasattr(self, 'processed_audio'):
            return
            
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Processed Audio",
            "",
            "WAV Files (*.wav);;All Files (*.*)"
        )
        
        if file_name:
            try:
                sf.write(file_name, self.processed_audio, self.sample_rate)
                self.status_label.setText(f"Saved to: {file_name}")
            except Exception as e:
                self.status_label.setText(f"Error saving file: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 