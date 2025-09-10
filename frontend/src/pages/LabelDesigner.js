import React, { useState, useRef } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Divider,
  Alert,
  Switch,
  FormControlLabel,
  Slider
} from '@mui/material';
import {
  Print as PrintIcon,
  Save as SaveIcon,
  Preview as PreviewIcon,
  Download as DownloadIcon
} from '@mui/icons-material';
import { useQuery, useMutation } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';

const LabelDesigner = () => {
  const [labelData, setLabelData] = useState({
    title: 'Sample Label',
    subtitle: 'Product Information',
    barcode: '123456789',
    qr_code: 'https://example.com',
    price: '$9.99',
    weight: '1.5 lbs',
    lot_code: 'LOT-20250105-001',
    expiry_date: '2025-12-31',
    company_name: 'Your Company',
    company_address: '123 Main St, City, State 12345',
    company_phone: '(555) 123-4567'
  });

  const [labelSettings, setLabelSettings] = useState({
    width: 4,
    height: 2,
    orientation: 'portrait',
    show_barcode: true,
    show_qr: true,
    show_price: true,
    show_weight: true,
    show_lot: true,
    show_expiry: true,
    font_size: 12,
    border_width: 1
  });

  const [previewMode, setPreviewMode] = useState(false);

  // Test print mutation
  const testPrintMutation = useMutation(
    (printData) => axios.post('/api/test-print', printData),
    {
      onSuccess: () => {
        toast.success('Test label printed successfully');
      },
      onError: (error) => {
        toast.error('Failed to print test label');
      }
    }
  );

  // Generate custom label mutation
  const generateLabelMutation = useMutation(
    (labelData) => axios.post('/api/custom-label/generate', labelData),
    {
      onSuccess: (response) => {
        toast.success('Label generated successfully');
        // Handle download or preview
      },
      onError: (error) => {
        toast.error('Failed to generate label');
      }
    }
  );

  const handleInputChange = (field, value) => {
    setLabelData({ ...labelData, [field]: value });
  };

  const handleSettingChange = (field, value) => {
    setLabelSettings({ ...labelSettings, [field]: value });
  };

  const handleTestPrint = () => {
    const printData = {
      ...labelData,
      settings: labelSettings
    };
    testPrintMutation.mutate(printData);
  };

  const handleGenerateLabel = () => {
    const fullData = {
      ...labelData,
      settings: labelSettings
    };
    generateLabelMutation.mutate(fullData);
  };

  const renderLabelPreview = () => {
    const { width, height, orientation } = labelSettings;
    const scale = orientation === 'landscape' ? 1.5 : 1;
    
    return (
      <Paper
        sx={{
          width: width * 50 * scale,
          height: height * 50 * scale,
          p: 2,
          border: `${labelSettings.border_width}px solid #000`,
          backgroundColor: 'white',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          fontSize: `${labelSettings.font_size}px`,
          fontFamily: 'monospace'
        }}
      >
        {/* Company Info */}
        <Box sx={{ textAlign: 'center', mb: 1 }}>
          <Typography variant="h6" sx={{ fontSize: `${labelSettings.font_size + 2}px`, fontWeight: 'bold' }}>
            {labelData.company_name}
          </Typography>
          <Typography variant="body2" sx={{ fontSize: `${labelSettings.font_size - 2}px` }}>
            {labelData.company_address}
          </Typography>
          <Typography variant="body2" sx={{ fontSize: `${labelSettings.font_size - 2}px` }}>
            {labelData.company_phone}
          </Typography>
        </Box>

        <Divider sx={{ my: 1 }} />

        {/* Product Info */}
        <Box sx={{ textAlign: 'center', mb: 1 }}>
          <Typography variant="h6" sx={{ fontSize: `${labelSettings.font_size + 1}px`, fontWeight: 'bold' }}>
            {labelData.title}
          </Typography>
          <Typography variant="body2" sx={{ fontSize: `${labelSettings.font_size}px` }}>
            {labelData.subtitle}
          </Typography>
        </Box>

        {/* Barcode/QR Section */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          {labelSettings.show_barcode && (
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body2" sx={{ fontSize: `${labelSettings.font_size - 2}px` }}>
                {labelData.barcode}
              </Typography>
              <Box sx={{ height: 20, backgroundColor: '#000', width: '100%' }} />
            </Box>
          )}
          {labelSettings.show_qr && (
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ width: 30, height: 30, backgroundColor: '#000', mx: 'auto' }} />
            </Box>
          )}
        </Box>

        {/* Product Details */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap' }}>
          {labelSettings.show_price && (
            <Typography variant="body2" sx={{ fontSize: `${labelSettings.font_size}px`, fontWeight: 'bold' }}>
              {labelData.price}
            </Typography>
          )}
          {labelSettings.show_weight && (
            <Typography variant="body2" sx={{ fontSize: `${labelSettings.font_size}px` }}>
              {labelData.weight}
            </Typography>
          )}
        </Box>

        {/* Lot and Expiry */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap' }}>
          {labelSettings.show_lot && (
            <Typography variant="body2" sx={{ fontSize: `${labelSettings.font_size - 2}px` }}>
              LOT: {labelData.lot_code}
            </Typography>
          )}
          {labelSettings.show_expiry && (
            <Typography variant="body2" sx={{ fontSize: `${labelSettings.font_size - 2}px` }}>
              EXP: {labelData.expiry_date}
            </Typography>
          )}
        </Box>
      </Paper>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Label Designer
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<PreviewIcon />}
            onClick={() => setPreviewMode(!previewMode)}
            sx={{ mr: 2 }}
          >
            {previewMode ? 'Hide Preview' : 'Show Preview'}
          </Button>
          <Button
            variant="contained"
            startIcon={<PrintIcon />}
            onClick={handleTestPrint}
            disabled={testPrintMutation.isLoading}
          >
            Test Print
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Label Content */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Label Content
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Title"
                    value={labelData.title}
                    onChange={(e) => handleInputChange('title', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Subtitle"
                    value={labelData.subtitle}
                    onChange={(e) => handleInputChange('subtitle', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Barcode"
                    value={labelData.barcode}
                    onChange={(e) => handleInputChange('barcode', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="QR Code URL"
                    value={labelData.qr_code}
                    onChange={(e) => handleInputChange('qr_code', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Price"
                    value={labelData.price}
                    onChange={(e) => handleInputChange('price', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Weight"
                    value={labelData.weight}
                    onChange={(e) => handleInputChange('weight', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Lot Code"
                    value={labelData.lot_code}
                    onChange={(e) => handleInputChange('lot_code', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Expiry Date"
                    type="date"
                    value={labelData.expiry_date}
                    onChange={(e) => handleInputChange('expiry_date', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Company Name"
                    value={labelData.company_name}
                    onChange={(e) => handleInputChange('company_name', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Company Address"
                    value={labelData.company_address}
                    onChange={(e) => handleInputChange('company_address', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Company Phone"
                    value={labelData.company_phone}
                    onChange={(e) => handleInputChange('company_phone', e.target.value)}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Label Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Label Settings
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Width (inches)"
                    type="number"
                    value={labelSettings.width}
                    onChange={(e) => handleSettingChange('width', parseFloat(e.target.value))}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Height (inches)"
                    type="number"
                    value={labelSettings.height}
                    onChange={(e) => handleSettingChange('height', parseFloat(e.target.value))}
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Orientation</InputLabel>
                    <Select
                      value={labelSettings.orientation}
                      onChange={(e) => handleSettingChange('orientation', e.target.value)}
                    >
                      <MenuItem value="portrait">Portrait</MenuItem>
                      <MenuItem value="landscape">Landscape</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <Typography gutterBottom>Font Size</Typography>
                  <Slider
                    value={labelSettings.font_size}
                    onChange={(e, value) => handleSettingChange('font_size', value)}
                    min={8}
                    max={20}
                    step={1}
                    marks
                    valueLabelDisplay="auto"
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography gutterBottom>Border Width</Typography>
                  <Slider
                    value={labelSettings.border_width}
                    onChange={(e, value) => handleSettingChange('border_width', value)}
                    min={0}
                    max={5}
                    step={1}
                    marks
                    valueLabelDisplay="auto"
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Display Options
                  </Typography>
                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={labelSettings.show_barcode}
                            onChange={(e) => handleSettingChange('show_barcode', e.target.checked)}
                          />
                        }
                        label="Barcode"
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={labelSettings.show_qr}
                            onChange={(e) => handleSettingChange('show_qr', e.target.checked)}
                          />
                        }
                        label="QR Code"
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={labelSettings.show_price}
                            onChange={(e) => handleSettingChange('show_price', e.target.checked)}
                          />
                        }
                        label="Price"
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={labelSettings.show_weight}
                            onChange={(e) => handleSettingChange('show_weight', e.target.checked)}
                          />
                        }
                        label="Weight"
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={labelSettings.show_lot}
                            onChange={(e) => handleSettingChange('show_lot', e.target.checked)}
                          />
                        }
                        label="Lot Code"
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={labelSettings.show_expiry}
                            onChange={(e) => handleSettingChange('show_expiry', e.target.checked)}
                          />
                        }
                        label="Expiry Date"
                      />
                    </Grid>
                  </Grid>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Preview */}
        {previewMode && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Label Preview
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                  {renderLabelPreview()}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default LabelDesigner;
