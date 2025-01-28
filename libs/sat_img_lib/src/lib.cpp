#include <Python.h>
#include <vector>
#include <cstring>

extern "C" {

// Convolution function
static PyObject* binary_convolve(PyObject* self, PyObject* args) {
    PyObject *matrix_obj, *kernel_obj;
    
    // Parse Python arguments: two 2D lists (matrix and kernel)
    if (!PyArg_ParseTuple(args, "OO", &matrix_obj, &kernel_obj)) {
        return NULL;
    }

    // Ensure the inputs are lists
    if (!PyList_Check(matrix_obj) || !PyList_Check(kernel_obj)) {
        PyErr_SetString(PyExc_TypeError, "Both arguments must be 2D lists");
        return NULL;
    }

    // Convert Python lists to 2D C++ vectors
    std::vector<std::vector<int>> matrix, kernel;
    Py_ssize_t rows = PyList_Size(matrix_obj);
    Py_ssize_t cols = PyList_Size(PyList_GetItem(matrix_obj, 0));
    Py_ssize_t kRows = PyList_Size(kernel_obj);
    Py_ssize_t kCols = PyList_Size(PyList_GetItem(kernel_obj, 0));

    // Convert Python lists to C++ vectors
    for (Py_ssize_t i = 0; i < rows; ++i) {
        PyObject* row = PyList_GetItem(matrix_obj, i);
        std::vector<int> row_vec;
        for (Py_ssize_t j = 0; j < cols; ++j) {
            row_vec.push_back(PyLong_AsLong(PyList_GetItem(row, j)));
        }
        matrix.push_back(row_vec);
    }

    for (Py_ssize_t i = 0; i < kRows; ++i) {
        PyObject* row = PyList_GetItem(kernel_obj, i);
        std::vector<int> row_vec;
        for (Py_ssize_t j = 0; j < kCols; ++j) {
            row_vec.push_back(PyLong_AsLong(PyList_GetItem(row, j)));
        }
        kernel.push_back(row_vec);
    }

    // Initialize result matrix
    std::vector<std::vector<int>> result(rows, std::vector<int>(cols, 0));
    int padRows = kRows / 2;
    int padCols = kCols / 2;

    // Perform convolution
    for (int i = padRows; i < rows - padRows; ++i) {
        for (int j = padCols; j < cols - padCols; ++j) {
            int sum = 0;
            for (int ki = 0; ki < kRows; ++ki) {
                for (int kj = 0; kj < kCols; ++kj) {
                    int mi = i + ki - padRows;
                    int mj = j + kj - padCols;
                    if (mi >= 0 && mi < rows && mj >= 0 && mj < cols) {
                        sum += matrix[mi][mj] * kernel[ki][kj];
                    }
                }
            }
            result[i][j] = sum;
        }
    }

    // Convert result back to Python list
    PyObject* result_list = PyList_New(rows);
    for (int i = 0; i < rows; ++i) {
        PyObject* row_list = PyList_New(cols);
        for (int j = 0; j < cols; ++j) {
            PyList_SetItem(row_list, j, PyLong_FromLong(result[i][j]));
        }
        PyList_SetItem(result_list, i, row_list);
    }

    return result_list;
}

// Define module methods
static PyMethodDef ConvolveMethods[] = {
    {"binary_convolve", binary_convolve, METH_VARARGS, "Perform binary convolution on two matrices"},
    {NULL, NULL, 0, NULL}
};

// Define module
static struct PyModuleDef convolve_module = {
    PyModuleDef_HEAD_INIT,
    "sat_img_lib",            // Module name
    "Simple library for image processing", // Module docstring
    -1,                       // Per-interpreter state
    ConvolveMethods           // Module methods
};

// Module initialization function
PyMODINIT_FUNC PyInit_sat_img_lib(void) {
    return PyModule_Create(&convolve_module);  // Use convolve_module here
}

}
