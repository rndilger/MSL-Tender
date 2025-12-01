import React, {useEffect, useMemo, useState} from 'react';
import {useTable, useSortBy, usePagination, useFilters, useRowSelect} from 'react-table';
import _ from 'lodash';

import './CreateSurvey.css';
import {useNavigate} from 'react-router-dom';
import {API_URL} from "../../util/util";

const IndeterminateCheckbox = React.forwardRef(
  ({indeterminate, ...rest}, ref) => {
    const defaultRef = React.useRef();
    const resolvedRef = ref || defaultRef;

    React.useEffect(() => {
      resolvedRef.current.indeterminate = indeterminate;
    }, [resolvedRef, indeterminate]);

    return (
      <>
        <input type="checkbox" ref={resolvedRef} {...rest} />
      </>
    );
  }
);

function DefaultColumnFilter({
                               column: {filterValue, preFilteredRows, setFilter},
                             }) {
  const count = preFilteredRows.length;

  return (
    <input
      className="tableFilterInput"
      value={filterValue || ''}
      onChange={e => {
        setFilter(e.target.value || undefined);
      }}
      placeholder={`Search ${count} records...`}
    />
  );
}

const CreateSurvey = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch(API_URL + "/surveys/data", {
      headers: {
        'Cache-Control': 'no-cache'
      }
    })
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        throw new Error('Network response was not ok.');
      })
      .then(res => {
        setData(res);
      })
      .catch(error => console.error('Failed to load data:', error));
  }, []);

  const columns = useMemo(() => [
    {
      id: 'selection',
      Header: ({getToggleAllRowsSelectedProps}) => (
        <div>
          <IndeterminateCheckbox {...getToggleAllRowsSelectedProps()} />
        </div>
      ),
      Cell: ({row}) => (
        <div>
          <IndeterminateCheckbox {...row.getToggleRowSelectedProps()} />
        </div>
      )
    },
    ...data[0] ? Object.keys(data[0]).map(key => {
      const filterableColumns = ['Study#', 'Original Chop ID', 'Standardized Chop ID', 'Block', 'Setting'];
      return {
        Header: key,
        accessor: key,
        Filter: filterableColumns.includes(key) ? DefaultColumnFilter : undefined,
        disableFilters: !filterableColumns.includes(key),
        width: 100
      };
    }) : []
  ], [data]);

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    page,
    selectedFlatRows,
    canPreviousPage,
    canNextPage,
    pageOptions,
    pageCount,
    gotoPage,
    nextPage,
    previousPage,
    setPageSize,
    state: {pageIndex, pageSize},
  } = useTable({
      columns,
      data,
      initialState: {pageIndex: 0}
    },
    useFilters,
    useSortBy,
    usePagination,
    useRowSelect,
    hooks => {
      hooks.visibleColumns.push(columns => [
        ...columns
      ]);
    });

  const navigate = useNavigate();

  const handleApply = () => {
    const standardizedChopIds = selectedFlatRows.map(row => row.original['Standardized Chop ID']);
    const shuffledChopIds = _.shuffle(standardizedChopIds).join(',');

    console.log(standardizedChopIds);
    console.log(shuffledChopIds);

    const postData = {
      chop_ids: shuffledChopIds
    };

    fetch(API_URL + '/surveys', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(postData)
    })
      .then(response => response.json())
      .then(data => {
        window.alert('Survey created successfully.');
        navigate("/surveys/" + data.id);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  };


  return (
    <>
      <div className="tableContainer">

        <table {...getTableProps()}>
          <thead>
          {headerGroups.map((headerGroup, index) => (
            <tr {...headerGroup.getHeaderGroupProps()} key={index}>
              {headerGroup.headers.map((column, colIndex) => (
                <th {...column.getHeaderProps()} key={colIndex}>
                  {column.render('Header')}
                  <div>{column.canFilter ? column.render('Filter') : null}</div>
                </th>
              ))}
            </tr>
          ))}
          </thead>
          <tbody {...getTableBodyProps()}>
          {page.map((row, rowIndex) => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()} key={rowIndex}>
                {row.cells.map((cell, cellIndex) => {
                  return <td {...cell.getCellProps()} key={cellIndex}>{cell.render('Cell')}</td>
                })}
              </tr>
            );
          })}
          </tbody>
        </table>
        <button className='apply' onClick={handleApply}
                disabled={selectedFlatRows.length === 0 || selectedFlatRows.length % 4 !== 0}>Create New Survey
        </button>
        <div className="pagination">
          <button onClick={() => gotoPage(0)} disabled={!canPreviousPage}>
            {'<<'}
          </button>
          <button onClick={() => previousPage()} disabled={!canPreviousPage}>
            {'<'}
          </button>
          <button onClick={() => nextPage()} disabled={!canNextPage}>
            {'>'}
          </button>
          <button onClick={() => gotoPage(pageCount - 1)} disabled={!canNextPage}>
            {'>>'}
          </button>
          <span>
          Page{' '}
            <strong>
            {pageIndex + 1} of {pageOptions.length}
          </strong>{' '}
        </span>
          <select
            value={pageSize}
            onChange={e => {
              setPageSize(Number(e.target.value));
            }}
          >
            {[10, 20, 30, 40, 50].map(pageSize => (
              <option key={pageSize} value={pageSize}>
                Show {pageSize}
              </option>
            ))}
          </select>
        </div>
      </div>
    </>
  );
};

export default CreateSurvey;
