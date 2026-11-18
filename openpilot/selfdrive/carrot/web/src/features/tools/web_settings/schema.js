"use strict";

// Web settings presentation schema. Value type, default, choices, and
// validation come only from services/web_settings.py. This file owns grouping,
// ordering, and translation keys for settings that should be user-visible.

const WEB_SETTINGS_GROUPS = [
  {
    id: "general",
    labelKey: "web_settings_general",
    items: [
      {
        id: "web_text_scale",
        titleKey: "web_text_scale",
        descKey: "web_text_scale_desc",
        options: [80, 90, 100, 110, 125, 150, 175, 200].map(value => ({ value: String(value), label: `${value}%` })),
      },
      {
        id: "auto_update_git_pull",
        titleKey: "web_auto_update",
        descKey: "web_auto_update_desc",
      },
      {
        id: "auto_update_reboot",
        titleKey: "web_auto_update_reboot",
        descKey: "web_auto_update_reboot_desc",
        options: [
          { value: "off", labelKey: "web_auto_update_reboot_off" },
          { value: "park", labelKey: "web_auto_update_reboot_park" },
          { value: "disengaged", labelKey: "web_auto_update_reboot_disengaged_or_offroad" },
        ],
      },
      {
        id: "start_page",
        titleKey: "web_start_page",
        descKey: "web_start_page_desc",
        options: [
          { value: "last", labelKey: "web_start_page_last" },
          { value: "carrot", labelKey: "home" },
          { value: "setting", labelKey: "setting" },
          { value: "tools", labelKey: "tools" },
          { value: "logs", labelKey: "logs" },
          { value: "terminal", labelKey: "terminal" },
        ],
      },
    ],
  },
  {
    id: "hud",
    labelKey: "web_settings_hud",
    items: [
      {
        id: "mini_hud_enabled",
        titleKey: "web_mini_hud_enabled",
        descKey: "web_mini_hud_enabled_desc",
      },
    ],
  },
  {
    id: "layout",
    labelKey: "web_settings_drive_layout",
    items: [
      {
        id: "carrot_navi_layout",
        component: "drive-layout",
      },
    ],
  },
  {
    id: "vision",
    labelKey: "web_settings_carrot_vision",
    items: [
      {
        id: "vision_stream_resolution",
        titleKey: "vision_stream_resolution",
        descKey: "vision_stream_resolution_desc",
        options: [
          { value: "standard", labelKey: "vision_quality_existing" },
          { value: "360", label: "360p" },
          { value: "540", label: "540p" },
          { value: "720", label: "720p" },
        ],
      },
      {
        id: "vision_render_quality",
        titleKey: "vision_render_quality",
        descKey: "vision_render_quality_desc",
        options: [
          { value: "auto", labelKey: "vision_quality_auto" },
          { value: "low", labelKey: "vision_quality_low" },
          { value: "standard", labelKey: "vision_quality_standard" },
          { value: "high", labelKey: "vision_quality_high" },
        ],
      },
      {
        id: "vision_presentation",
        titleKey: "vision_live_presentation",
        descKey: "vision_live_description",
        options: [
          { value: "carrot", labelKey: "vision_live_classic" },
          { value: "live_view", labelKey: "vision_live_name" },
          { value: "tesla", labelKey: "vision_tesla_name" },
          { value: "bev", labelKey: "bev_name" },
        ],
      },
      {id:"vision_custom_metrics",titleKey:"vision_custom_metrics",descKey:"vision_custom_metrics_desc"},
      {id:"vision_rainbow_lane",titleKey:"vision_rainbow_lane",descKey:"vision_rainbow_lane_desc"},
      {id:"vision_parking_assist",titleKey:"vision_parking_assist",descKey:"vision_parking_assist_desc"},
      {id:"vision_parking_map",titleKey:"vision_parking_map",descKey:"vision_parking_map_desc"},
      {id:"vision_vehicle_color",titleKey:"vision_vehicle_color",descKey:"vision_vehicle_color_desc",options:["white","silver","gray","black","red","blue","green","beige","orange"].map(value=>({value,labelKey:`vehicle_color_${value}`}))},
      {id:"vision_object_detection",titleKey:"scene_detection",descKey:"scene_detection_desc"},
      {id:"vision_road_detection",titleKey:"road_detection",descKey:"road_detection_desc"},
      {id:"vision_bev_range",titleKey:"bev_range",descKey:"bev_range_desc",options:[30,50,75].map(n=>({value:String(n),label:`${n} m`}))},
      {id:"vision_bev_grid",titleKey:"bev_grid",descKey:"bev_grid_desc"},
      {id:"vision_bev_details",titleKey:"bev_details",descKey:"bev_details_desc"},
      {id:"recording_quota_percent",titleKey:"recording_quota_percent",descKey:"recording_quota_percent_desc",
        options:[{value:"0",labelKey:"recording_quota_off"},...[10,20,30,40,50,60,70,80,90].map(v=>({value:String(v),label:`${v}%`}))]},
      {
        id: "vision_fullscreen_default",
        titleKey: "web_vision_fullscreen_default",
        descKey: "web_vision_fullscreen_default_desc",
      },
      {
        id: "vision_ar_enabled",
        titleKey: "web_vision_ar_enabled",
        descKey: "web_vision_ar_enabled_desc",
      },
      {
        id: "vision_ar_debug",
        titleKey: "web_vision_ar_debug",
        descKey: "web_vision_ar_debug_desc",
      },
    ],
  },
  {
    id: "navigation",
    labelKey: "web_settings_navigation",
    items: [
      {
        id: "carrot_navi_fullscreen_on_tap",
        titleKey: "web_navi_fullscreen_on_tap",
        descKey: "web_navi_fullscreen_on_tap_desc",
      },
      {
        id: "carrot_navi_map_appearance",
        component: "param-selects",
        fields: [
          {
            id: "carrot_navi_map_type",
            paramName: "ClusterNaviMapType",
            titleKey: "web_navi_map_type",
            descKey: "web_navi_map_type_desc",
            options: [
              { value: "0", labelKey: "web_navi_map_type_normal" },
              { value: "1", labelKey: "web_navi_map_type_satellite" },
            ],
          },
          {
            id: "carrot_navi_map_theme",
            paramName: "ClusterNaviMapTheme",
            titleKey: "web_navi_map_theme",
            descKey: "web_navi_map_theme_desc",
            options: [
              { value: "0", labelKey: "web_navi_map_theme_auto" },
              { value: "1", labelKey: "web_navi_map_theme_dark" },
              { value: "2", labelKey: "web_navi_map_theme_light" },
            ],
          },
        ],
      },
    ],
  },
  {
    id: "upload",
    labelKey: "web_settings_upload",
    items: [
      {
        id: "web_upload",
        component: "web-upload",
      },
    ],
  },
];

window.WEB_SETTINGS_GROUPS = WEB_SETTINGS_GROUPS;

export { WEB_SETTINGS_GROUPS };
