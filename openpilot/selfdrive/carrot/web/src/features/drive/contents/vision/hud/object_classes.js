// Exact names verified against labels.txt in the pinned EfficientDet model.
export const ANIMALS=Object.freeze(['cat','dog','horse','sheep','cow','elephant','bear','zebra','giraffe']);
export const ROAD_CLASSES=Object.freeze(['person','bicycle','car','motorcycle','bus','truck',...ANIMALS]);
// Birds may fly; signs/lights are elevated. Never intersect their boxes with
// the ground plane to invent a 3D location or assign a traffic-light colour.
export const IMAGE_ONLY_CLASSES=Object.freeze(['bird','traffic light','stop sign']);
export const DETECTOR_CLASSES=Object.freeze([...ROAD_CLASSES,...IMAGE_ONLY_CLASSES]);
export const OBJECT_NAMES=Object.freeze({person:'行人',bicycle:'腳踏車',car:'汽車',motorcycle:'機車',bus:'巴士',truck:'卡車',cat:'貓',dog:'狗',horse:'馬',sheep:'羊',cow:'牛',elephant:'大象',bear:'熊',zebra:'斑馬',giraffe:'長頸鹿',bird:'鳥', 'traffic light':'交通號誌（未判讀燈色）','stop sign':'STOP 停止標誌'});
