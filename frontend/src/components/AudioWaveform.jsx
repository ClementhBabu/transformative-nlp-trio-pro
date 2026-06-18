import React, { useRef, useEffect } from 'react';
import { Box, useTheme } from '@mui/material';

function AudioWaveform({ audioUrl, isPlaying = false, color, height = 80 }) {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const theme = useTheme();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();

    canvas.width = rect.width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    const width = rect.width;
    const barColor = color || theme.palette.primary.main;
    const barCount = 48;
    const barWidth = (width / barCount) - 2;

    const draw = () => {
      ctx.clearRect(0, 0, width, height);

      for (let i = 0; i < barCount; i++) {
        let barHeight;
        if (isPlaying) {
          const t = Date.now() / 180;
          barHeight = (Math.sin(t + i * 0.4) * 0.5 + 0.5) * (height - 8) + 4;
          barHeight += (Math.sin(t * 2.3 + i * 0.6) * 0.3) * (height - 8);
        } else {
          barHeight = (Math.sin(i * 0.5) * 0.3 + 0.5) * (height * 0.3) + 2;
        }

        const x = i * (barWidth + 2);
        const y = height - Math.max(4, barHeight);

        ctx.fillStyle = barColor;
        ctx.fillRect(x, y, barWidth, Math.max(4, barHeight));
      }

      animationRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [isPlaying, color, height, theme.palette.primary.main]);

  return (
    <Box sx={{ width: '100%' }}>
      <canvas
        ref={canvasRef}
        style={{
          width: '100%',
          height,
          borderRadius: 8,
        }}
      />
    </Box>
  );
}

export default AudioWaveform;
