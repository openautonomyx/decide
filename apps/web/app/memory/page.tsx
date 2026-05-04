'use client';

import { useMemory } from '@/lib/hooks';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Database, Search, Plus, Eye } from 'lucide-react';
import { useState } from 'react';

export default function MemoryPage() {
  const { data: memory, isLoading } = useMemory();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMemory, setSelectedMemory] = useState<string | null>(null);

  const filteredMemory = memory?.filter(
    (m) =>
      m.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const selectedMemoryItem = memory?.find((m) => m.id === selectedMemory);

  const getTypeBadge = (type: string) => {
    const colors: Record<string, string> = {
      preference: 'bg-blue-100 text-blue-800',
      conversation: 'bg-purple-100 text-purple-800',
      faq: 'bg-green-100 text-green-800',
      knowledge: 'bg-yellow-100 text-yellow-800',
    };
    return (
      <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${colors[type] || 'bg-gray-100 text-gray-800'}`}>
        {type}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Memory</h1>
          <p className="text-muted-foreground">
            View and manage stored memories
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add Memory
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>All Memories</CardTitle>
              <CardDescription>
                {isLoading
                  ? 'Loading memories...'
                  : `${filteredMemory?.length || 0} memories stored`}
              </CardDescription>
            </div>
            <div className="relative w-64">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search memories..."
                className="pl-8"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Type</TableHead>
                <TableHead>Content</TableHead>
                <TableHead>Created</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center">
                    Loading...
                  </TableCell>
                </TableRow>
              ) : filteredMemory && filteredMemory.length > 0 ? (
                filteredMemory.map((mem) => (
                  <TableRow key={mem.id}>
                    <TableCell>{getTypeBadge(mem.type)}</TableCell>
                    <TableCell className="max-w-md truncate">
                      {mem.content}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {new Date(mem.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedMemory(mem.id)}
                      >
                        <Eye className="mr-1 h-3 w-3" />
                        View
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={4} className="text-center">
                    No memories found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Detail Dialog */}
      <Dialog open={!!selectedMemory} onOpenChange={() => setSelectedMemory(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Memory Details</DialogTitle>
            <DialogDescription>
              View full memory content and metadata
            </DialogDescription>
          </DialogHeader>
          {selectedMemoryItem && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                {getTypeBadge(selectedMemoryItem.type)}
              </div>
              <div className="rounded-md bg-muted p-4">
                <p className="whitespace-pre-wrap">{selectedMemoryItem.content}</p>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">ID</p>
                  <p className="font-mono">{selectedMemoryItem.id}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Created</p>
                  <p>{new Date(selectedMemoryItem.created_at).toLocaleString()}</p>
                </div>
                {selectedMemoryItem.metadata && Object.keys(selectedMemoryItem.metadata).length > 0 && (
                  <div className="col-span-2">
                    <p className="text-muted-foreground">Metadata</p>
                    <pre className="mt-1 rounded-md bg-muted p-2 font-mono text-xs">
                      {JSON.stringify(selectedMemoryItem.metadata, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}