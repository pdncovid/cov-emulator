import React, { useState, useRef } from "react"
import { useTable, usePagination, useResizeColumns, useBlockLayout } from 'react-table'

// import styled from 'styled-components'
// const Styles = styled.div`
//   padding: 1rem;

//   .table {
//     display: inline-block;
//     border-spacing: 0;
//     border: 1px solid black;

//     .tr {
//       :last-child {
//         .td {
//           border-bottom: 0;
//         }
//       }
//     }

//     .th,
//     .td {
//       margin: 0;
//       padding: 0.5rem;
//       border-bottom: 1px solid black;
//       border-right: 1px solid black;

//       ${'' /* In this example we use an absolutely position resizer,
//        so this is required. */}
//       position: relative;

//       :last-child {
//         border-right: 0;
//       }

//       .resizer {
//         display: inline-block;
//         background: blue;
//         width: 10px;
//         height: 100%;
//         position: absolute;
//         right: 0;
//         top: 0;
//         transform: translateX(50%);
//         z-index: 1;
//         ${'' /* prevents from scrolling while dragging on touch devices */}
//         touch-action:none;

//         &.isResizing {
//           background: red;
//         }
//       }
//     }
//   }
// `

// Create an editable cell renderer
const EditableCell = ({
    value: initialValue,
    row: { index },
    column: { id },
    updateMyData, // This is a custom function that we supplied to our table instance
}) => {
    // We need to keep and update the state of the cell normally
    const [value, setValue] = React.useState(initialValue)

    const onChange = e => {
        setValue(e.target.value)
    }

    // We'll only update the external data when the input is blurred
    const onBlur = () => {
        updateMyData(index, id, value)
    }

    // If the initialValue is changed external, sync it up with our state
    React.useEffect(() => {
        setValue(initialValue)
    }, [initialValue])

    return <input value={value} onChange={onChange} onBlur={onBlur} />
}

// Set our editable cell renderer as the default Cell renderer
const defaultColumn = {
    Cell: EditableCell,
    minWidth: 30,
    width: 150,
    maxWidth: 400,
}


// Be sure to pass our updateMyData and the skipPageReset option
const Table = ({ columns, data, updateMyData, skipPageReset, addNewRow, onSave }) => {
    // For this example, we're using pagination to illustrate how to stop
    // the current page from resetting when our data changes
    // Otherwise, nothing is different here.
    const {
        getTableProps,
        getTableBodyProps,
        headerGroups,
        prepareRow,
        page,
        canPreviousPage,
        canNextPage,
        pageOptions,
        pageCount,
        gotoPage,
        nextPage,
        previousPage,
        setPageSize,
        rows,
        resetResizing,
        state: { pageIndex, pageSize },
    } = useTable(
        {
            columns,
            data,
            defaultColumn,
            autoResetPage: !skipPageReset,
            updateMyData,
        },
        usePagination,
        useBlockLayout,
        useResizeColumns
    )

    // Render the UI for your table
    return (
        <>{/*
        
            <div>
                <div {...getTableProps()} className="table">
                    <div>
                        {headerGroups.map(headerGroup => (
                            <div {...headerGroup.getHeaderGroupProps()} className="tr">
                                {headerGroup.headers.map(column => (
                                    <div {...column.getHeaderProps()} className="th">
                                        {column.render('Header')}
                                        <div
                                            {...column.getResizerProps()}
                                            className={`resizer ${column.isResizing ? 'isResizing' : ''
                                                }`}
                                        />
                                    </div>
                                ))}
                            </div>
                        ))}
                    </div>

                    <div {...getTableBodyProps()}>
                        {page.map((row, i) => {
                            prepareRow(row)
                            return (
                                <tr {...row.getRowProps()}>
                                    {row.cells.map(cell => {
                                        return <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
                                    })}
                                </tr>
                            )
                        })}
                    </div>
                </div>
            </div>
        */}
            <table {...getTableProps()}>
                <thead>
                    {headerGroups.map(headerGroup => (
                        <tr {...headerGroup.getHeaderGroupProps()}>
                            {headerGroup.headers.map(column => (
                                <th {...column.getHeaderProps()}>{column.render('Header')}</th>
                            ))}
                        </tr>
                    ))}
                </thead>

                <tbody {...getTableBodyProps()}>
                    {page.map((row, i) => {
                        prepareRow(row)
                        return (
                            <tr {...row.getRowProps()}>
                                {row.cells.map(cell => {
                                    return <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
                                })}
                            </tr>
                        )
                    })}
                </tbody>
            </table>
            
            <div className="pagination">
                <button onClick={() => gotoPage(0)} disabled={!canPreviousPage}>
                    {'<<'}
                </button>{' '}
                <button onClick={() => previousPage()} disabled={!canPreviousPage}>
                    {'<'}
                </button>{' '}
                <button onClick={() => nextPage()} disabled={!canNextPage}>
                    {'>'}
                </button>{' '}
                <button onClick={() => gotoPage(pageCount - 1)} disabled={!canNextPage}>
                    {'>>'}
                </button>{' '}
                <span>
                    Page{' '}
                    <strong>
                        {pageIndex + 1} of {pageOptions.length}
                    </strong>{' '}
                </span>
                <span>
                    | Go to page:{' '}
                    <input
                        type="number"
                        defaultValue={pageIndex + 1}
                        onChange={e => {
                            const page = e.target.value ? Number(e.target.value) - 1 : 0
                            gotoPage(page)
                        }}
                        style={{ width: '100px' }}
                    />
                </span>{' '}
                <select
                    value={pageSize}
                    onChange={e => {
                        setPageSize(Number(e.target.value))
                    }}
                >
                    {[10, 20, 30, 40, 50].map(pageSize => (
                        <option key={pageSize} value={pageSize}>
                            Show {pageSize}
                        </option>
                    ))}
                </select>
                {addNewRow != undefined && (<button onClick={() => addNewRow()}>{'+'}</button>)}{' '}
                {onSave!=undefined && (<button onClick={() => onSave()}>
                    {'Save'}
                </button>)}{' '}
            </div>
        </>
    )
}

export default Table;