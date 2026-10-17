import { EntitySchema, EntitySchemaColumnOptions } from 'typeorm';
import definitions from './schema.json';
import { z } from 'zod';

export type Row = Record<string, string | number | Date | null>;
export interface Field { type: string; length?: number; nullable?: boolean }
export interface TableSpec { table: string; keys: string[]; fields: Record<string, Field> }
export const tables: TableSpec[] = z.array(z.object({
  table: z.string(), keys: z.array(z.string()),
  fields: z.record(z.string(), z.object({
    type: z.enum(['integer', 'decimal', 'string', 'date']),
    length: z.number().optional(), nullable: z.boolean().optional(),
  })),
})).parse(definitions);
// EntitySchema mantiene nombres SQL explicitos sin sincronizar ni recrear el DDL.
export const entities = tables.map(spec => new EntitySchema<Row>({
  name: spec.table,
  tableName: spec.table,
  schema: 'dbo',
  columns: Object.fromEntries(Object.entries(spec.fields).map(([name, field]) => {
    const column: EntitySchemaColumnOptions = {
      type: ({ integer: 'int', decimal: 'decimal', string: 'nvarchar', date: 'datetime2' } as Record<string, 'int' | 'decimal' | 'nvarchar' | 'datetime2'>)[field.type],
      primary: spec.keys.includes(name),
      nullable: field.nullable ?? false,
    };
    if (field.length) column.length = field.length;
    if (field.type === 'decimal') { column.precision = 12; column.scale = 2; }
    if (field.type === 'date') column.precision = 0;
    return [name, column];
  })),
}));
