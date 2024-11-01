/**
 * This file was auto-generated by openapi-typescript.
 * Do not make direct changes to the file.
 */


export type paths = {
  "/task/{task_id}/generator": {
    /** Get Generator */
    get: operations["get_generator_task__task_id__generator_get"];
    /** Add Generator */
    post: operations["add_generator_task__task_id__generator_post"];
  };
  "/task/{task_id}/generator/{generator_id}": {
    /** Get Generator */
    get: operations["get_generator_task__task_id__generator__generator_id__get"];
    /** Update Generator */
    put: operations["update_generator_task__task_id__generator__generator_id__put"];
    /** Start Generator */
    post: operations["start_generator_task__task_id__generator__generator_id__post"];
    /** Update Generator */
    delete: operations["update_generator_task__task_id__generator__generator_id__delete"];
  };
  "/task/{task_id}/generator/{generator_id}/clearOutput": {
    /** Clear Output */
    put: operations["clear_output_task__task_id__generator__generator_id__clearOutput_put"];
  };
  "/task/{task_id}/generate/barChart": {
    /** Start Bar Chart */
    post: operations["start_bar_chart_task__task_id__generate_barChart_post"];
  };
  "/task/image/preview/line": {
    /** Preview Line Image */
    post: operations["preview_line_image_task_image_preview_line_post"];
  };
  "/task": {
    /** Get Task */
    get: operations["get_task_task_get"];
    /** Add Task */
    post: operations["add_task_task_post"];
  };
  "/task/{task_id}": {
    /** Update Task Name */
    put: operations["update_task_name_task__task_id__put"];
    /** Remove Task File */
    delete: operations["remove_task_file_task__task_id__delete"];
  };
  "/task/{task_id}/file": {
    /** Get Task File */
    get: operations["get_task_file_task__task_id__file_get"];
    /** Add Task File */
    post: operations["add_task_file_task__task_id__file_post"];
  };
  "/task/{task_id}/file/{task_file_id}": {
    /** Update Task File */
    put: operations["update_task_file_task__task_id__file__task_file_id__put"];
    /** Remove Task File */
    delete: operations["remove_task_file_task__task_id__file__task_file_id__delete"];
  };
  "/health": {
    /** Health */
    get: operations["health_health_get"];
  };
  "/merge": {
    /** Merge */
    post: operations["merge_merge_post"];
  };
};

export type webhooks = Record<string, never>;

export type components = {
  schemas: {
    /** BarChartGeneratorStartRequest */
    BarChartGeneratorStartRequest: {
      /** Generatorids */
      generatorIds: number[];
      /** Chartname */
      chartName: string | null;
      /** Comparegroup */
      compareGroup: number[][][];
      /**
       * Xlabel
       * @default 测点
       */
      xLabel?: string | null;
      /**
       * Ylabel
       * @default 值
       */
      yLabel?: string | null;
      /**
       * Xrotation
       * @default -45
       */
      xRotation?: number | null;
      /**
       * Width
       * @default 0.35
       */
      width?: number;
    };
    /**
     * ChartFillEnum
     * @enum {string}
     */
    ChartFillEnum: "FORWARD_FILL" | "BACKWARD_FILL" | "NONE" | "LINE" | "TIME";
    /** DauConfig */
    DauConfig: {
      /** Column */
      column: string;
      /** Mapping */
      mapping: number;
    };
    /** GeneratorAllResponse */
    GeneratorAllResponse: {
      /** Name */
      name: string;
      /** Id */
      id: number;
      /**
       * Createddate
       * Format: date-time
       */
      createdDate: string;
      /**
       * Updateddate
       * Format: date-time
       */
      updatedDate: string;
      /** Files */
      files: string | null;
      /** @default PROCESSING */
      status?: components["schemas"]["GeneratorResultEnum"];
      /** Result */
      result: string | null;
      configObj: components["schemas"]["GeneratorConfigRequest-Output"] | null;
      /** Output */
      output: string | null;
    };
    /** GeneratorConfigRequest */
    "GeneratorConfigRequest-Input": {
      /** Converters */
      converters: components["schemas"]["GeneratorDataConverterRequest-Input"][];
      /** Dauconfig */
      dauConfig: components["schemas"]["DauConfig"][] | null;
      /**
       * Dateformat
       * @default %Y-%m-%d-%H-%M-%S.%f
       */
      dateFormat?: string | null;
    };
    /** GeneratorConfigRequest */
    "GeneratorConfigRequest-Output": {
      /** Converters */
      converters: components["schemas"]["GeneratorDataConverterRequest-Output"][];
      /** Dauconfig */
      dauConfig: components["schemas"]["DauConfig"][] | null;
      /**
       * Dateformat
       * @default %Y-%m-%d-%H-%M-%S.%f
       */
      dateFormat?: string | null;
    };
    /** GeneratorCreateRequest */
    GeneratorCreateRequest: {
      /** Name */
      name: string;
      /** Files */
      files: string;
      configObj: components["schemas"]["GeneratorConfigRequest-Input"] | null;
    };
    /** GeneratorDataCondition */
    GeneratorDataCondition: {
      type: components["schemas"]["GeneratorDataConditionType"];
      /** Value */
      value: number;
      /**
       * Starttime
       * Format: date-time
       */
      startTime: string;
      /**
       * Endtime
       * Format: date-time
       */
      endTime: string;
    };
    /**
     * GeneratorDataConditionType
     * @enum {string}
     */
    GeneratorDataConditionType: "MAX" | "MIN";
    /** GeneratorDataConverterRequest */
    "GeneratorDataConverterRequest-Input": {
      /** Columnkey */
      columnKey: string;
      /** Expression */
      expression: string;
      /**
       * Conditions
       * @default []
       */
      conditions?: components["schemas"]["GeneratorDataCondition"][] | null;
    };
    /** GeneratorDataConverterRequest */
    "GeneratorDataConverterRequest-Output": {
      /** Columnkey */
      columnKey: string;
      /** Expression */
      expression: string;
      /**
       * Conditions
       * @default []
       */
      conditions?: components["schemas"]["GeneratorDataCondition"][] | null;
    };
    /** GeneratorResponse */
    GeneratorResponse: {
      /** Name */
      name: string;
      /** Id */
      id: number;
      /**
       * Createddate
       * Format: date-time
       */
      createdDate: string;
      /**
       * Updateddate
       * Format: date-time
       */
      updatedDate: string;
      /** Files */
      files: string | null;
      /** @default PROCESSING */
      status?: components["schemas"]["GeneratorResultEnum"];
      /** Result */
      result: string | null;
      configObj: components["schemas"]["GeneratorConfigRequest-Output"] | null;
    };
    /**
     * GeneratorResultEnum
     * @enum {string}
     */
    GeneratorResultEnum: "SUCCESS" | "PROCESSING" | "FAILED" | "WAITING";
    /** HTTPValidationError */
    HTTPValidationError: {
      /** Detail */
      detail?: components["schemas"]["ValidationError"][];
    };
    /** HealthResponse */
    HealthResponse: {
      /** Status */
      status: string;
    };
    /** LineChartRequest */
    LineChartRequest: {
      /** Generate */
      generate: boolean;
      /**
       * Columnindex
       * @default []
       */
      columnIndex?: number[];
      /**
       * Timerange
       * @default 10T
       */
      timeRange?: string;
      /** Xlabel */
      xLabel: string;
      /** Ylabel */
      yLabel: string;
      /** Xrotation */
      xRotation: number;
      /** Name */
      name: string[];
      fill?: components["schemas"]["ChartFillEnum"] | null;
      /**
       * Linewidth
       * @default 1
       */
      lineWidth?: number;
      /**
       * Showgrid
       * @default true
       */
      showGrid?: boolean;
    };
    /** MergeBase */
    MergeBase: {
      /** Filepath */
      filePath: string;
      /** Column */
      column: string;
    };
    /** MergeConfig */
    MergeConfig: {
      /**
       * Removebasenull
       * @default true
       */
      removeBaseNull?: boolean;
      /**
       * Removenull
       * @default false
       */
      removeNull?: boolean;
    };
    /** MergeFiles */
    MergeFiles: {
      /** Filepath */
      filePath: string;
      /** Selectcolumns */
      selectColumns: string[];
    };
    /** MergeRequest */
    MergeRequest: {
      base: components["schemas"]["MergeBase"] | null;
      /** Files */
      files: components["schemas"]["MergeFiles"][];
      config: components["schemas"]["MergeConfig"] | null;
    };
    /** PreviewImageRequest */
    PreviewImageRequest: {
      /**
       * Chartxlabel
       * @default X 轴
       */
      chartXLabel?: string;
      /**
       * Chartylabel
       * @default Y 轴
       */
      chartYLabel?: string;
      /**
       * Charttimerange
       * @default 10T
       */
      chartTimeRange?: string;
      /**
       * Chartxrotation
       * @default 0
       */
      chartXRotation?: number;
      /**
       * Chartname
       * @default 示例图
       */
      chartName?: string;
      /**
       * Chartlinewidth
       * @default 1
       */
      chartLineWidth?: number;
      /**
       * Chartdatanumber
       * @default 1000
       */
      chartDataNumber?: number;
      chartFill?: components["schemas"]["ChartFillEnum"] | null;
      /**
       * Chartshowgrid
       * @default true
       */
      chartShowGrid?: boolean;
    };
    /** TaskCreateRequest */
    TaskCreateRequest: {
      /** Name */
      name: string;
    };
    /** TaskFileCreateRequest */
    TaskFileCreateRequest: {
      /** Names */
      names: string[];
    };
    /** TaskFileResponse */
    TaskFileResponse: {
      /** Name */
      name: string;
      /** Id */
      id: number;
      /** Taskid */
      taskId: number;
      /**
       * Createddate
       * Format: date-time
       */
      createdDate: string;
      /**
       * Updateddate
       * Format: date-time
       */
      updatedDate: string;
    };
    /** TaskFileUpdateRequest */
    TaskFileUpdateRequest: {
      /** Name */
      name: string;
    };
    /** TaskGeneratorStartRequest */
    TaskGeneratorStartRequest: {
      averageLineChart: components["schemas"]["LineChartRequest"];
      maxMinLineChart: components["schemas"]["LineChartRequest"];
      rootMeanSquareLineChart: components["schemas"]["LineChartRequest"];
      rawLineChart: components["schemas"]["LineChartRequest"];
      config?: components["schemas"]["GeneratorConfigRequest-Input"] | null;
      /** Savedata */
      saveData: boolean;
      /** Averagebarchart */
      averageBarChart: boolean;
      /** Maxminbarchart */
      maxMinBarChart: boolean;
      /** Averagedatatable */
      averageDataTable: boolean;
      /** Maxmindatatable */
      maxMinDataTable: boolean;
      /** Rootmeansquaredatatable */
      rootMeanSquareDataTable: boolean;
      /** Rawdatatable */
      rawDataTable: boolean;
      /** Averagebargroup */
      averageBarGroup: number[][];
      /** Maxminbargroup */
      maxMinBarGroup: number[][];
    };
    /** TaskResponse */
    TaskResponse: {
      /** Name */
      name: string;
      /** Id */
      id: number;
      /**
       * Createddate
       * Format: date-time
       */
      createdDate: string;
      /**
       * Updateddate
       * Format: date-time
       */
      updatedDate: string;
    };
    /** ValidationError */
    ValidationError: {
      /** Location */
      loc: (string | number)[];
      /** Message */
      msg: string;
      /** Error Type */
      type: string;
    };
  };
  responses: never;
  parameters: never;
  requestBodies: never;
  headers: never;
  pathItems: never;
};

export type $defs = Record<string, never>;

export type external = Record<string, never>;

export type operations = {

  /** Get Generator */
  get_generator_task__task_id__generator_get: {
    parameters: {
      path: {
        task_id: number;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["GeneratorResponse"][];
        };
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Add Generator */
  add_generator_task__task_id__generator_post: {
    parameters: {
      path: {
        task_id: number;
      };
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["GeneratorCreateRequest"];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["GeneratorResponse"];
        };
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Get Generator */
  get_generator_task__task_id__generator__generator_id__get: {
    parameters: {
      path: {
        task_id: number;
        generator_id: number;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["GeneratorAllResponse"];
        };
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Update Generator */
  update_generator_task__task_id__generator__generator_id__put: {
    parameters: {
      path: {
        task_id: number;
        generator_id: number;
      };
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["GeneratorCreateRequest"];
      };
    };
    responses: {
      /** @description Successful Response */
      204: {
        content: never;
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Start Generator */
  start_generator_task__task_id__generator__generator_id__post: {
    parameters: {
      path: {
        task_id: number;
        generator_id: number;
      };
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["TaskGeneratorStartRequest"];
      };
    };
    responses: {
      /** @description Successful Response */
      204: {
        content: never;
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Update Generator */
  update_generator_task__task_id__generator__generator_id__delete: {
    parameters: {
      path: {
        generator_id: number;
      };
    };
    responses: {
      /** @description Successful Response */
      204: {
        content: never;
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Clear Output */
  clear_output_task__task_id__generator__generator_id__clearOutput_put: {
    parameters: {
      path: {
        task_id: number;
        generator_id: number;
      };
    };
    responses: {
      /** @description Successful Response */
      204: {
        content: never;
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Start Bar Chart */
  start_bar_chart_task__task_id__generate_barChart_post: {
    parameters: {
      path: {
        task_id: number;
      };
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["BarChartGeneratorStartRequest"];
      };
    };
    responses: {
      /** @description Successful Response */
      204: {
        content: never;
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Preview Line Image */
  preview_line_image_task_image_preview_line_post: {
    requestBody: {
      content: {
        "application/json": components["schemas"]["PreviewImageRequest"];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": unknown;
        };
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Get Task */
  get_task_task_get: {
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["TaskResponse"][];
        };
      };
    };
  };
  /** Add Task */
  add_task_task_post: {
    requestBody: {
      content: {
        "application/json": components["schemas"]["TaskCreateRequest"];
      };
    };
    responses: {
      /** @description Successful Response */
      201: {
        content: {
          "application/json": components["schemas"]["TaskResponse"];
        };
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Update Task Name */
  update_task_name_task__task_id__put: {
    parameters: {
      path: {
        task_id: number;
      };
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["TaskCreateRequest"];
      };
    };
    responses: {
      /** @description Successful Response */
      204: {
        content: never;
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Remove Task File */
  remove_task_file_task__task_id__delete: {
    parameters: {
      path: {
        task_id: number;
      };
    };
    responses: {
      /** @description Successful Response */
      204: {
        content: never;
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Get Task File */
  get_task_file_task__task_id__file_get: {
    parameters: {
      path: {
        task_id: number;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["TaskFileResponse"][];
        };
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Add Task File */
  add_task_file_task__task_id__file_post: {
    parameters: {
      path: {
        task_id: number;
      };
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["TaskFileCreateRequest"];
      };
    };
    responses: {
      /** @description Successful Response */
      201: {
        content: {
          "application/json": unknown;
        };
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Update Task File */
  update_task_file_task__task_id__file__task_file_id__put: {
    parameters: {
      path: {
        task_id: number;
        task_file_id: number;
      };
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["TaskFileUpdateRequest"];
      };
    };
    responses: {
      /** @description Successful Response */
      204: {
        content: never;
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Remove Task File */
  remove_task_file_task__task_id__file__task_file_id__delete: {
    parameters: {
      path: {
        task_id: number;
        task_file_id: number;
      };
    };
    responses: {
      /** @description Successful Response */
      204: {
        content: never;
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Health */
  health_health_get: {
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["HealthResponse"];
        };
      };
    };
  };
  /** Merge */
  merge_merge_post: {
    requestBody: {
      content: {
        "application/json": components["schemas"]["MergeRequest"];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": unknown;
        };
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
};
