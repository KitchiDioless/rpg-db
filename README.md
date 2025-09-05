![:D]((https://i.pinimg.com/736x/ec/03/67/ec0367b08a085bf6ede2d9fd39cbe3cf.jpg))

## Entity

> Обобщенная сущность. Имеет уникальный id, может взаимодействовать с миром и обладает такими характеристиками как имя, раса, гендер и уровень.

- entity_id : int \<PK>

- name : varchar

- race_id : int \<FK>

- gender : enum

- level : int

## Character

> Npc. Имеет свой уникальный id, id сущности и id домашней локации, где он будет находиться по умолчанию.

- character_id : int \<PK>

- entity_id : int \<FK> \<UNIQUE>

- home_location_id : int \<FK>

## Player

> Игрок. Имеет свой уникальный id и координаты последнего сохранения на случай выхода из игры, загрузки или вылета. Имеет доступ к журналу игрока.

- player_id : int \<PK>

- entity_id : int \<FK> \<UNIQUE>

- last_save_coords_x : float

- last_save_coords_y : float

- last_save_coords_z : float

## PlayerJournal

> Журнал игрока с записями, каждая запись имеет id, id игрока, текст и дату изменения.

- event_id : int \<PK>

- player_id : int \<FK>

- date : datetime

- text : text

## Location

> Локация. Имеет название, тип и 2D границы в мире. 

- location_id : int \<PK>

- name : varchar

- type : varchar

- bound_coord_x : float

- bound_coord_y : float

## Race

> Раса сущности. Имеет название и расовые бонусы.

- race_id : int \<PK>

- name : varchar

- bonuses : text


## Faction

> Фракции, существующие в мире. Имеют id и название.

- faction_id : int \<PK>

- name : varchar

## CharacterFaction

> Фракция npc. Содержит id фракции, id npc, его репутацию в этой фракции и титул. 

- entity_id : int \<PK> \<FK>

- faction_id : int \<PK> \<FK>

- reputation : int

- title : varchar

## Quest

> Квест. Состоит из id, названия и описания. Может быть выдан npc.

- quest_id : int \<PK>

- name : varchar

- description : text

## CharacterQuest

> Конкретный квест выдаваемый конкретным npc. Содержит id сущности, id квеста и статус завершения.

- entity_id : int \<PK> \<FK>

- quest_id : int \<PK> \<FK>

- status : enum

## Skill

> Навык, которым могут обладать сущности. Имеет id, название и описание.

- skill_id : int \<PK>

- name : varchar

- description : text

## EntitySkill

> Навык конкретной сущности, имеет id сущности, id навыка и уровень навыка.

- entity_id : int \<PK> \<FK>

- skill_id : int \<PK> \<FK>

- level : int

## Spell

> Заклинание, которое могут использовать сущности. Имеет id, название, описание и эффект.

- spell_id : int \<PK>

- name : varchar

- mana_cost : int

- effect : text

## EntitySpell

> Заклинание конкретной сущности, имеет id сущности и id заклинания.

- entity_id : int \<PK> \<FK>

- spell_id : int \<PK> \<FK>

## Dialogue

> Диалог, который можно завести с npc. Обладает id, id сущности к которой прикреплен диалог, текст диалога и результат.

- dialogue_id : int \<PK>

- entity_id : int \<FK>

- text : text

- response_type : enum

## Item

> Предмет. Имеет id, название, вес, цену и тип. Если тип броня или оружие, то он может иметь зачарование.

- item_id : int \<PK>

- name : varchar

- weight : float

- cost : int

- type : enum <<weapon, armor, misc>>

## EntityInventory

> Инвентарь сущности. В нем находятся все предметы. Имеет id сущности, id предмета и количество.

- entity_id : int \<PK> \<FK>

- item_id : int \<PK> \<FK>

- quantity : int

## EnchantableItem

> Предмет который можно зачаровать. Имеет id предмета, и id зачарования.

- item_id : int \<PK> \<FK>

- enchantment_id : int \<FK>

## UnenchantableItem

> Предмет который нельзя зачаровать. Имеет id предмета и описание использования.

- item_id : int \<PK> \<FK>

- usage : text

## Enchantment

> Зачарование. Может быть наложено на некоторые объекты. Имеет id зачарования, название, описание и оставшееся количесво использований.

- enchantment_id : int \<PK>

- name : varchar

- description : text

- charges : int

## EnchantmentEffect

> Эффект конкретного зачарования. Состоит из id эффекта, id зачарования, типа эффекта и продолжительности.

- effect_id : int \<PK>

- enchantment_id : int \<FK>

- effect_type : varchar

- duration : int

```plantuml
entity Entity {
  * entity_id : int <<PK>>
  --
  name : varchar
  race_id : int <<FK>>
  gender : enum
  level : int
}

entity Character {
  * character_id : int <<PK>>
  --
  entity_id : int <<FK>> <<UNIQUE>>
  home_location_id : int <<FK>>
}

entity Player {
  * player_id : int <<PK>>
  --
  entity_id : int <<FK>> <<UNIQUE>>
  last_save_coords_x : float
  last_save_coords_y : float
  last_save_coords_z : float
}

entity PlayerJournal {
  * event_id : int <<PK>>
  --
  player_id : int <<FK>>
  date : datetime
  text : text
}

entity Location {
  * location_id : int <<PK>>
  --
  name : varchar
  type : varchar
  bound_coord_x : float
  bound_coord_y : float
}

entity Race {
  * race_id : int <<PK>>
  --
  name : varchar
  bonuses : text
}

entity Faction {
  * faction_id : int <<PK>>
  --
  name : varchar
}

entity CharacterFaction {
  * entity_id : int <<PK>> <<FK>>
  * faction_id : int <<PK>> <<FK>>
  reputation : int
  title : varchar
}

entity Quest {
  * quest_id : int <<PK>>
  --
  name : varchar
  description : text
}

entity CharacterQuest {
  * entity_id : int <<PK>> <<FK>>
  * quest_id : int <<PK>> <<FK>>
  status : enum
}

entity Skill {
  * skill_id : int <<PK>>
  --
  name : varchar
  description : text
}

entity EntitySkill {
  * entity_id : int <<PK>> <<FK>>
  * skill_id : int <<PK>> <<FK>>
  level : int
}

entity Spell {
  * spell_id : int <<PK>>
  --
  name : varchar
  mana_cost : int
  effect : text
}

entity EntitySpell {
  * entity_id : int <<PK>> <<FK>>
  * spell_id : int <<PK>> <<FK>>
}

entity Dialogue {
  * dialogue_id : int <<PK>>
  --
  entity_id : int <<FK>>
  text : text
  response_type : enum
}

entity Item {
  * item_id : int <<PK>>
  --
  name : varchar
  weight : float
  cost : int
  type : enum <<weapon, armor, misc>>
}

entity EntityInventory {
  * entity_id : int <<PK>> <<FK>>
  * item_id : int <<PK>> <<FK>>
  quantity : int
}

entity EnchantableItem {
  * item_id : int <<PK>> <<FK>>
  --
  enchantment_id : int <<FK>> <<nullable>>
}

entity UnenchantableItem {
  * item_id : int <<PK>> <<FK>>
  --
  usage : text
}

entity Enchantment {
  * enchantment_id : int <<PK>>
  --
  name : varchar
  description : text
  charges : int
}

entity EnchantmentEffect {
  * effect_id : int <<PK>>
  --
  enchantment_id : int <<FK>>
  effect_type : varchar
  duration : int
}

Entity ||--o{ Race : race  
Character ||--|| Entity : is  
Character }o--|| Location : home_location  
Player ||--|| Entity : is  
PlayerJournal }o--|| Player  
CharacterFaction }|--|| Character  
CharacterFaction }|--|| Faction  
CharacterQuest }|--|| Character  
CharacterQuest }|--|| Quest  
EntitySkill }|--|| Entity  
EntitySkill }|--|| Skill  
EntitySpell }|--|| Entity  
EntitySpell }|--|| Spell  
Dialogue }o--|| Entity  
EntityInventory }|--|| Entity  
EntityInventory }|--|| Item  
EnchantableItem ||--|| Item  
UnenchantableItem ||--|| Item  
EnchantableItem }o--|| Enchantment  
EnchantmentEffect }o--|| Enchantment
```
